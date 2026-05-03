from __future__ import annotations

import json
import logging
import time
from typing import Any

from google.genai import types

from claims_pipeline.config import get_settings
from claims_pipeline.llm.base import LLMProvider

logger = logging.getLogger(__name__)

_ALLOWED_FALLBACK = "OTHERS"

# Re-call Gemini when response is not parseable JSON or wrong shape (model occasionally violates MIME JSON).
_JSON_COMPLETION_MAX_ATTEMPTS = 3


def _decode_first_json_value(text: str) -> Any:
    """Parse the first JSON value from model output.

    Gemini sometimes appends a second JSON object or prose after the first,
    which makes json.loads fail with JSONDecodeError: Extra data.
    """
    if not text or not text.strip():
        return None
    s = text.strip()
    if s.startswith("```"):
        lines = s.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    decoder = json.JSONDecoder()
    for i, ch in enumerate(s):
        if ch not in "{[":
            continue
        try:
            val, _ = decoder.raw_decode(s[i:])
            return val
        except json.JSONDecodeError:
            continue
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def _normalize_doc_label(raw: str | None, allowed: frozenset[str]) -> str | None:
    if not raw or not isinstance(raw, str):
        return None
    u = raw.strip().upper().replace(" ", "_").replace("-", "_")
    if u in allowed:
        return u
    aliases = {
        "RX": "PRESCRIPTION",
        "PRESCRIPTION_PAD": "PRESCRIPTION",
        "CONSULTATION_PRESCRIPTION": "PRESCRIPTION",
        "INVOICE": "HOSPITAL_BILL",
        "BILL": "HOSPITAL_BILL",
        "ITEMIZED_BILL": "HOSPITAL_BILL",
        "LAB": "LAB_REPORT",
        "PATHOLOGY": "LAB_REPORT",
        "PHARMACY_INVOICE": "PHARMACY_BILL",
    }
    alt = aliases.get(u)
    if alt and alt in allowed:
        return alt
    if _ALLOWED_FALLBACK in allowed:
        return _ALLOWED_FALLBACK
    return None


class GeminiProvider(LLMProvider):
    """Google Gemini structured extraction (vision optional)."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        s = get_settings()
        self.api_key = api_key or s.gemini_api_key
        self.model = model or s.llm_model
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)

    def _with_json_retry_prompt(self, base_contents: list[Any], attempt: int) -> list[Any]:
        """Duplicate base contents and append stricter JSON instructions on retries."""
        if attempt == 0:
            return base_contents
        hint = (
            "\n\nCRITICAL — PREVIOUS OUTPUT WAS INVALID OR UNPARSEABLE:\n"
            "Reply with exactly ONE JSON object only. No markdown fences, no commentary, "
            "no second JSON object, no trailing text after the closing brace.\n"
        )
        out = list(base_contents)
        if out and isinstance(out[0], str):
            out[0] = out[0] + hint
        return out

    def _generate_json_value(
        self,
        base_contents: list[Any],
        *,
        claim_id: str,
        operation: str,
        require_dict: bool = True,
    ) -> tuple[Any | None, str]:
        """Call Gemini with application/json; retry up to N times on decode/type failure."""
        last_text = ""
        for attempt in range(_JSON_COMPLETION_MAX_ATTEMPTS):
            contents = self._with_json_retry_prompt(base_contents, attempt)
            try:
                resp = self._client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                text = resp.text or "{}"
                last_text = text
                raw = _decode_first_json_value(text)
                if raw is None:
                    logger.warning(
                        "Gemini %s JSON decode failed attempt %s/%s claim=%s",
                        operation,
                        attempt + 1,
                        _JSON_COMPLETION_MAX_ATTEMPTS,
                        claim_id,
                    )
                    continue
                if require_dict and not isinstance(raw, dict):
                    logger.warning(
                        "Gemini %s JSON not an object attempt %s/%s claim=%s type=%s",
                        operation,
                        attempt + 1,
                        _JSON_COMPLETION_MAX_ATTEMPTS,
                        claim_id,
                        type(raw).__name__,
                    )
                    continue
                return raw, text
            except Exception as e:
                logger.warning(
                    "Gemini %s API error attempt %s/%s claim=%s: %s",
                    operation,
                    attempt + 1,
                    _JSON_COMPLETION_MAX_ATTEMPTS,
                    claim_id,
                    e,
                )
                continue
        return None, last_text

    def extract_document(
        self,
        claim_id: str,
        file_id: str,
        doc_type: str,
        image_bytes: bytes | None,
        mime_type: str | None,
        hint: str,
    ) -> tuple[dict[str, Any], float]:
        self._ensure_client()
        prompt = (
            f"You extract structured data from a medical document image.\n"
            f"Document type hint: {doc_type}\n"
            "Your JSON MUST include a top-level object `_meta` first (same object), then fields:\n"
            "`_meta`: {\n"
            '  "confidence": <number 0-1, how sure you are that extracted values are correct>,\n'
            '  "readability": "GOOD" | "UNREADABLE",\n'
            '  "notes": "<short explanation citing blur, glare, crop, or missing sections>"\n'
            "}\n"
            "If the photo is too blurry or text cannot be read reliably, set readability to UNREADABLE, "
            "confidence low (e.g. under 0.45), use null for uncertain fields, and explain in notes.\n"
            "Outside `_meta`, include keys appropriate for this doc type: "
            "patient_name, doctor_name, doctor_registration, diagnosis, date, "
            "medicines (array), line_items (array of {description, amount}), "
            "total, hospital_name, tests_ordered (array), etc.\n"
            f"Extra hint: {hint}\n"
        )
        contents: list[Any] = [prompt]
        if image_bytes:
            contents.append(
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg")
            )

        t0 = time.perf_counter()
        raw, _text = self._generate_json_value(
            contents,
            claim_id=claim_id,
            operation=f"extract:{file_id}",
            require_dict=True,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        if raw is None or not isinstance(raw, dict):
            logger.error(
                "Gemini extract JSON exhausted retries claim=%s file=%s ms=%s",
                claim_id,
                file_id,
                latency_ms,
            )
            return {}, 0.35
        meta = raw.pop("_meta", None)
        if isinstance(meta, dict):
            raw["_extraction_meta"] = meta
            conf = float(meta.get("confidence", 0.85 if image_bytes else 0.75))
        else:
            conf = 0.85 if image_bytes else 0.75
        conf = max(0.0, min(1.0, conf))
        logger.info("Gemini extract ok claim=%s file=%s ms=%s", claim_id, file_id, latency_ms)
        return raw, conf

    def classify_document_type(
        self,
        claim_id: str,
        file_id: str,
        image_bytes: bytes,
        mime_type: str | None,
        allowed_labels: list[str],
    ) -> tuple[str | None, float]:
        allowed = frozenset(x.upper() for x in allowed_labels if x)
        if not allowed:
            return None, 0.0
        self._ensure_client()
        lines = "\n".join(f"- {x}" for x in sorted(allowed))
        prompt = (
            "You classify a photo of a medical/financial document from an Indian healthcare context.\n"
            "Pick exactly ONE label from the list below — copy the token exactly (uppercase, underscores).\n\n"
            f"{lines}\n\n"
            "Guidance:\n"
            "- PRESCRIPTION: doctor Rx pad, diagnosis, medicines; clinic prescription layout.\n"
            "- HOSPITAL_BILL: printed itemized bill with line amounts and total from hospital/clinic.\n"
            "- PHARMACY_BILL: pharmacy/chemist receipt.\n"
            "- LAB_REPORT: pathology report with test names and results.\n"
            "- DISCHARGE_SUMMARY: discharge document from inpatient stay.\n"
            "- DIAGNOSTIC_REPORT: imaging/report narrative (CT/MRI/USG summary).\n"
            "- DENTAL_REPORT: dental chart or dental-specific clinical report.\n"
            "- OTHERS: none of the above or unreadable/photo of something else.\n\n"
            "Return ONLY valid JSON: {\"document_type\":\"<LABEL>\",\"confidence\":0.95}\n"
            "confidence must be between 0 and 1.\n"
        )
        contents: list[Any] = [prompt]
        contents.append(
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg")
        )
        t0 = time.perf_counter()
        payload, _text = self._generate_json_value(
            contents,
            claim_id=claim_id,
            operation=f"classify:{file_id}",
            require_dict=True,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        if payload is None or not isinstance(payload, dict):
            logger.error(
                "Gemini classify JSON exhausted retries claim=%s file=%s ms=%s",
                claim_id,
                file_id,
                latency_ms,
            )
            return None, 0.35
        raw_label = payload.get("document_type") or payload.get("label")
        conf = float(payload.get("confidence", 0.85))
        conf = max(0.0, min(1.0, conf))
        label = _normalize_doc_label(str(raw_label) if raw_label is not None else None, allowed)
        if label is None:
            logger.warning(
                "Gemini classify bad label claim=%s file=%s raw=%r ms=%s",
                claim_id,
                file_id,
                raw_label,
                latency_ms,
            )
            return None, 0.4
        logger.info(
            "Gemini classify ok claim=%s file=%s label=%s ms=%s",
            claim_id,
            file_id,
            label,
            latency_ms,
        )
        return label, conf

    def assess_waiting_period_clinical(
        self,
        claim_id: str,
        clinical_bundle: str,
        condition_catalog: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], float]:
        """Text-only medical adjudication: extracted clinical snippets vs insurer waiting-period buckets."""
        self._ensure_client()
        catalog_lines = "\n".join(
            f'- "{c.get("condition_key")}" (~{c.get("waiting_period_days")} days): {c.get("scope", "")}'
            for c in condition_catalog
        )
        prompt = (
            "You are an experienced clinician assisting Indian health insurance claims review.\n"
            "You receive structured text extracted from claim documents (prescriptions, bills, lab summaries). "
            "You must NOT invent diagnoses or treatments not supported by the bundle.\n\n"
            "TASK: For each policy bucket below, decide whether the clinical picture shown in the bundle "
            "plausibly relates to care FOR that condition or clearly indicated treatment typical of that "
            "condition (medicines, procedures, diagnoses).\n"
            "Use conservative judgment: if evidence is vague or only incidental (e.g. routine CBC), "
            'mark unrelated or low confidence.\n\n'
            "POLICY WAITING-PERIOD DISEASE BUCKETS (exact condition_key tokens):\n"
            f"{catalog_lines}\n\n"
            "EXTRACTED CLINICAL BUNDLE (JSON):\n"
            f"{clinical_bundle}\n\n"
            "Return ONE JSON object:\n"
            "{\n"
            '  "matches": [\n'
            "    {\n"
            '      "condition_key": "<must be one of the exact tokens listed>",\n'
            '      "related": true/false,\n'
            '      "confidence": <0-1>,\n'
            '      "clinical_evidence": "<short: cite diagnoses, drugs, or procedures from the bundle>"\n'
            "    }\n"
            "  ],\n"
            '  "insufficient_clinical_information": true/false,\n'
            '  "review_notes": "<optional caveats>"\n'
            "}\n"
            "Include every bucket you evaluated with related=false where appropriate, "
            "OR only include positives — prefer listing positives with related=true plus confidence.\n"
            "If the bundle has almost no clinical detail, set insufficient_clinical_information true "
            "and use empty matches or very low confidence.\n"
        )
        t0 = time.perf_counter()
        raw, _text = self._generate_json_value(
            [prompt],
            claim_id=claim_id,
            operation="waiting_period_clinical",
            require_dict=True,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
        if raw is None or not isinstance(raw, dict):
            logger.error(
                "Gemini waiting-period clinical JSON exhausted retries claim=%s ms=%s",
                claim_id,
                latency_ms,
            )
            return {"matches": [], "insufficient_clinical_information": True, "source": "error"}, 0.4
        try:
            matches = raw.get("matches")
            if not isinstance(matches, list):
                matches = []
            allowed = {str(c.get("condition_key")) for c in condition_catalog if c.get("condition_key")}
            cleaned: list[dict[str, Any]] = []
            for m in matches:
                if not isinstance(m, dict):
                    continue
                key = str(m.get("condition_key", "")).strip()
                if key not in allowed:
                    continue
                related = bool(m.get("related"))
                try:
                    cf = float(m.get("confidence", 0.7))
                except (TypeError, ValueError):
                    cf = 0.5
                cf = max(0.0, min(1.0, cf))
                ev = m.get("clinical_evidence")
                cleaned.append(
                    {
                        "condition_key": key,
                        "related": related,
                        "confidence": cf,
                        "clinical_evidence": str(ev) if ev is not None else "",
                    }
                )
            out = {
                "matches": cleaned,
                "insufficient_clinical_information": bool(
                    raw.get("insufficient_clinical_information", False)
                ),
                "review_notes": raw.get("review_notes"),
                "source": "gemini_clinical",
            }
            # Headline confidence: max related match confidence or 0.75
            pos = [x["confidence"] for x in cleaned if x.get("related")]
            conf = max(pos) if pos else 0.75
            logger.info(
                "Gemini waiting-period clinical ok claim=%s matches=%s ms=%s",
                claim_id,
                len(cleaned),
                latency_ms,
            )
            return out, conf
        except Exception as e:
            logger.exception("Gemini waiting-period clinical post-parse failed: %s", e)
            return {"matches": [], "insufficient_clinical_information": True, "source": "error"}, 0.4
