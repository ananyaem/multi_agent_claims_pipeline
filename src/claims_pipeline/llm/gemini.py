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
        try:
            resp = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            text = resp.text or "{}"
            raw = json.loads(text)
            if not isinstance(raw, dict):
                raw = {}
            meta = raw.pop("_meta", None)
            if isinstance(meta, dict):
                raw["_extraction_meta"] = meta
                conf = float(meta.get("confidence", 0.85 if image_bytes else 0.75))
            else:
                conf = 0.85 if image_bytes else 0.75
            conf = max(0.0, min(1.0, conf))
            logger.info("Gemini extract ok claim=%s file=%s ms=%s", claim_id, file_id, latency_ms)
            return raw, conf
        except Exception as e:
            logger.exception("Gemini extract failed: %s", e)
            return {}, 0.35

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
        try:
            resp = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            latency_ms = int((time.perf_counter() - t0) * 1000)
            text = resp.text or "{}"
            payload = json.loads(text)
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
        except Exception as e:
            logger.exception("Gemini classify failed: %s", e)
            return None, 0.35
