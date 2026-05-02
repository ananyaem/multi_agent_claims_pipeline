from __future__ import annotations

import json
import logging
import time
from typing import Any

from google.genai import types

from claims_pipeline.config import get_settings
from claims_pipeline.llm.base import LLMProvider

logger = logging.getLogger(__name__)


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
            f"Return ONLY valid JSON with keys appropriate for this doc type: "
            f"patient_name, doctor_name, doctor_registration, diagnosis, date, "
            f"medicines (array), line_items (array of {{description, amount}}), "
            f"total, hospital_name, tests_ordered (array), etc.\n"
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
            data = json.loads(text)
            conf = 0.85 if image_bytes else 0.75
            logger.info("Gemini extract ok claim=%s file=%s ms=%s", claim_id, file_id, latency_ms)
            return data, conf
        except Exception as e:
            logger.exception("Gemini extract failed: %s", e)
            return {}, 0.35
