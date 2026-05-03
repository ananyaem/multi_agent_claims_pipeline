from __future__ import annotations

from typing import Any, Protocol

from claims_pipeline.config import get_settings, upload_root_path
from claims_pipeline.pipeline.context import PipelineContext
from claims_pipeline.policy import PolicyService


class LLMExtractor(Protocol):
    def extract_document(
        self,
        claim_id: str,
        file_id: str,
        doc_type: str,
        raw_bytes: bytes | None,
        mime_type: str | None,
        hint: str,
    ) -> tuple[dict[str, Any], float]:
        ...


def _strip_llm_internal_keys(data: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if not str(k).startswith("_")}


def _non_empty_extraction(data: dict[str, Any]) -> bool:
    """True if at least one field has a non-null, non-empty value."""
    for v in data.values():
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        if isinstance(v, (list, dict)) and len(v) == 0:
            continue
        return True
    return False


def _extraction_usable(ed: dict[str, Any], floor: float) -> bool:
    conf = float(ed.get("extraction_confidence") or 0)
    data = ed.get("data") or {}
    return conf >= floor and _non_empty_extraction(data)


def _enforce_required_extraction_quality(ctx: PipelineContext) -> None:
    """Halt if policy-required document types have unusable LLM extraction (empty / very low confidence)."""
    if ctx.halted_reason:
        return
    svc = PolicyService(ctx.policy_terms)
    cat = (ctx.submission.get("claim_category") or "").upper()
    required = svc.document_requirements(cat).get("required") or []
    if not required:
        return
    floor = float(get_settings().extraction_usable_confidence_floor)

    for r in required:
        matches = [e for e in ctx.extracted_documents if (e.get("actual_type") or "").upper() == r]
        if not matches:
            continue
        if any(_extraction_usable(e, floor) for e in matches):
            continue
        bad = next((e for e in matches if not _extraction_usable(e, floor)), matches[0])
        fname = bad.get("file_name") or bad.get("file_id") or r
        ctx.halted_reason = "EXTRACTION_INCOMPLETE"
        ctx.member_message = (
            f"We could not reliably read required information from “{fname}” "
            f"({r.replace('_', ' ').title()}). Please re-upload a clearer photo or PDF."
        )
        ctx.halt_details = {
            "document_type": r,
            "file_id": bad.get("file_id"),
            "extraction_confidence": bad.get("extraction_confidence"),
            "reason": "empty_or_low_confidence",
        }
        return


def run_extraction(ctx: PipelineContext, llm: LLMExtractor | None) -> None:
    """Populate extracted_documents from fixture content or LLM."""
    ran_vision_llm = False
    for doc in ctx.submission.get("documents", []):
        fid = doc.get("file_id", "")
        fname = doc.get("file_name")
        dtype = doc.get("actual_type") or "UNKNOWN"
        if doc.get("content") is not None:
            row = {
                "file_id": fid,
                "file_name": fname,
                "actual_type": dtype,
                "data": doc["content"],
                "extraction_confidence": 0.94,
                "extraction_meta": {
                    "source": "fixture_content",
                    "readability": "GOOD",
                    "confidence": 0.94,
                    "notes": "Structured content supplied by test harness (not from vision).",
                },
            }
            if doc.get("patient_name_on_doc"):
                row["patient_name_on_doc"] = doc["patient_name_on_doc"]
            ctx.extracted_documents.append(row)
            ctx.add_step_confidence(0.94, step=f"ExtractionAgent:{fid}")
            continue
        raw_bytes: bytes | None = None
        mime = doc.get("mime_type")
        rel = doc.get("storage_relpath")
        if rel:
            path = upload_root_path() / rel
            try:
                if path.is_file() and path.resolve().is_relative_to(upload_root_path().resolve()):
                    raw_bytes = path.read_bytes()
            except (OSError, ValueError):
                raw_bytes = None

        if llm is None:
            ctx.degraded_components.append("ExtractionAgent")
            row = {
                "file_id": fid,
                "file_name": fname,
                "actual_type": dtype,
                "data": {},
                "extraction_confidence": 0.4,
                "extraction_meta": None,
            }
            if doc.get("patient_name_on_doc"):
                row["patient_name_on_doc"] = doc["patient_name_on_doc"]
            ctx.extracted_documents.append(row)
            ctx.add_step_confidence(0.4, step=f"ExtractionAgent:{fid}")
            continue
        ran_vision_llm = True
        data, conf = llm.extract_document(ctx.claim_id, fid, dtype, raw_bytes, mime, "")
        meta = data.pop("_extraction_meta", None)
        clean = _strip_llm_internal_keys(data)
        # Retry once when the model returns empty JSON or very low confidence (avoids silent policy skips).
        retry_hint = (
            "Repeat extraction: previous output was empty or unreliable. "
            "Return a single JSON object with `_meta` and every field you can read from the image."
        )
        if raw_bytes and (not _non_empty_extraction(clean) or conf < 0.52):
            data2, conf2 = llm.extract_document(
                ctx.claim_id, fid, dtype, raw_bytes, mime, retry_hint
            )
            meta2 = data2.pop("_extraction_meta", None)
            clean2 = _strip_llm_internal_keys(data2)
            better = _non_empty_extraction(clean2) and (
                not _non_empty_extraction(clean) or conf2 > conf or len(clean2) > len(clean)
            )
            if better or (_non_empty_extraction(clean2) and not _non_empty_extraction(clean)):
                data, conf, meta, clean = data2, conf2, meta2, clean2

        row = {
            "file_id": fid,
            "file_name": fname,
            "actual_type": dtype,
            "data": clean,
            "extraction_confidence": conf,
            "extraction_meta": meta if isinstance(meta, dict) else None,
        }
        if doc.get("patient_name_on_doc"):
            row["patient_name_on_doc"] = doc["patient_name_on_doc"]
        ctx.extracted_documents.append(row)
        ctx.add_step_confidence(conf, step=f"ExtractionAgent:{fid}")

    if ran_vision_llm:
        _enforce_required_extraction_quality(ctx)
