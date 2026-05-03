"""LLM agent: relate extracted clinical evidence to policy-specific waiting-period diseases."""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from claims_pipeline.pipeline.context import PipelineContext

logger = logging.getLogger(__name__)

# Short gloss for the model — keys MUST match policy_terms.waiting_periods.specific_conditions
_CONDITION_GUIDANCE: dict[str, str] = {
    "diabetes": "Diabetes mellitus (type 1 or 2), diabetic complications routine care, anti-diabetic medications.",
    "hypertension": "Hypertension / high BP management, typical antihypertensive therapy.",
    "thyroid_disorders": "Hypothyroidism, hyperthyroidism, thyroid hormone therapy or antithyroid drugs.",
    "joint_replacement": "Elective hip/knee/major joint replacement surgery or clearly pre-operative workup solely for arthroplasty.",
    "maternity": "Pregnancy, childbirth, prenatal/postnatal obstetric care — not general GYN unless clearly maternity.",
    "mental_health": "Psychiatric or psychological treatment, antidepressants/antipsychotics/anxiolytics for chronic mental health conditions.",
    "obesity_treatment": "Medically supervised obesity treatment, anti-obesity drugs, bariatric pathways — not casual diet advice.",
    "hernia": "Hernia repair or clearly hernia-specific surgical evaluation.",
    "cataract": "Cataract evaluation/surgery or definitive cataract-related procedures.",
}


class WaitingPeriodClinicalLLM(Protocol):
    def assess_waiting_period_clinical(
        self,
        claim_id: str,
        clinical_bundle: str,
        condition_catalog: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], float]:
        ...


def _catalog_from_policy(terms: dict[str, Any]) -> list[dict[str, Any]]:
    spec = (terms.get("waiting_periods") or {}).get("specific_conditions") or {}
    out: list[dict[str, Any]] = []
    for key, days in spec.items():
        if not isinstance(key, str):
            continue
        try:
            d = int(days)
        except (TypeError, ValueError):
            continue
        out.append(
            {
                "condition_key": key,
                "waiting_period_days": d,
                "scope": _CONDITION_GUIDANCE.get(
                    key,
                    "Treatments typically associated with this condition per standard Indian health insurance practice.",
                ),
            }
        )
    return sorted(out, key=lambda x: x["condition_key"])


def _compact_clinical_payload(ctx: PipelineContext) -> list[dict[str, Any]]:
    """Structured clinical hints from extractions (no raw images)."""
    blocks: list[dict[str, Any]] = []
    for ed in ctx.extracted_documents:
        d = ed.get("data") or {}
        meta = ed.get("extraction_meta") if isinstance(ed.get("extraction_meta"), dict) else {}
        block: dict[str, Any] = {
            "document_type": ed.get("actual_type"),
            "file_name": ed.get("file_name"),
            "diagnosis": d.get("diagnosis"),
            "chief_complaint": d.get("chief_complaint"),
            "medicines": d.get("medicines"),
            "tests_ordered": d.get("tests_ordered"),
            "line_items": d.get("line_items"),
            "doctor_notes": d.get("doctor_notes"),
            "extraction_confidence": ed.get("extraction_confidence"),
            "readability_note": meta.get("notes") if meta else None,
        }
        blocks.append(block)
    return blocks


def _fallback_assess(ctx: PipelineContext, catalog: list[dict[str, Any]]) -> tuple[dict[str, Any], float]:
    """Offline/tests when no LLM: conservative keyword checks only (does not replace medical agent in production)."""
    allowed = {c["condition_key"] for c in catalog}
    matches: list[dict[str, Any]] = []
    blob = json.dumps(_compact_clinical_payload(ctx), ensure_ascii=False).lower()

    def add(key: str, evidence: str, conf: float) -> None:
        if key in allowed:
            matches.append(
                {
                    "condition_key": key,
                    "related": True,
                    "confidence": conf,
                    "clinical_evidence": evidence,
                }
            )

    if "diabetes" in allowed and (
        "diabetes" in blob or "diabet" in blob or "metformin" in blob or "glimepiride" in blob
    ):
        add("diabetes", "Fallback keyword signal (no medical LLM in this run).", 0.72)
    if "hypertension" in allowed and (
        "hypertension" in blob or "amlodipine" in blob or "losartan" in blob or "blood pressure" in blob
    ):
        add("hypertension", "Fallback keyword signal (no medical LLM in this run).", 0.65)

    return (
        {
            "matches": matches,
            "insufficient_clinical_information": len(matches) == 0,
            "review_notes": "Heuristic fallback — configure LLM for clinical waiting-period review.",
            "source": "fallback_keywords",
        },
        0.7 if matches else 0.55,
    )


def run_waiting_period_medical_review(ctx: PipelineContext, llm: WaitingPeriodClinicalLLM | None) -> None:
    catalog = _catalog_from_policy(ctx.policy_terms)
    if not catalog:
        ctx.waiting_period_medical = {"matches": [], "source": "no_catalog"}
        return

    bundle = json.dumps(_compact_clinical_payload(ctx), ensure_ascii=False, indent=2)
    if not bundle or bundle == "[]":
        ctx.waiting_period_medical = {
            "matches": [],
            "insufficient_clinical_information": True,
            "review_notes": "No extracted clinical fields.",
            "source": "empty_bundle",
        }
        ctx.add_step_confidence(0.88, step="WaitingPeriodMedicalAgent")
        return

    if llm is None:
        payload, conf = _fallback_assess(ctx, catalog)
        payload["source"] = payload.get("source") or "fallback_keywords"
        ctx.waiting_period_medical = payload
        ctx.add_step_confidence(conf, step="WaitingPeriodMedicalAgent")
        return

    try:
        payload, conf = llm.assess_waiting_period_clinical(ctx.claim_id, bundle, catalog)
    except Exception:
        logger.exception("WaitingPeriodMedicalAgent LLM failure; using fallback")
        payload, conf = _fallback_assess(ctx, catalog)
        payload["source"] = "fallback_after_error"
        ctx.degraded_components.append("WaitingPeriodMedicalAgent")

    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("matches", [])
    ctx.waiting_period_medical = payload
    ctx.add_step_confidence(max(0.5, min(1.0, conf)), step="WaitingPeriodMedicalAgent")
