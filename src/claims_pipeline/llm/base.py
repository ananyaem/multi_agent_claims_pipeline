from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract extraction provider (Gemini, OpenAI, Claude, …)."""

    @abstractmethod
    def extract_document(
        self,
        claim_id: str,
        file_id: str,
        doc_type: str,
        image_bytes: bytes | None,
        mime_type: str | None,
        hint: str,
    ) -> tuple[dict[str, Any], float]:
        """Return structured extraction dict and confidence in [0,1]."""

    def classify_document_type(
        self,
        claim_id: str,
        file_id: str,
        image_bytes: bytes,
        mime_type: str | None,
        allowed_labels: list[str],
    ) -> tuple[str | None, float]:
        """Vision-only document family label. Return None if not implemented."""
        return None, 0.0

    def assess_waiting_period_clinical(
        self,
        claim_id: str,
        clinical_bundle: str,
        condition_catalog: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], float]:
        """Medical review of extracted clinical text vs policy waiting-period disease keys."""
        return {"matches": [], "insufficient_clinical_information": True}, 0.5


class FakeLLMProvider(LLMProvider):
    """Stub for tests — returns empty."""

    def extract_document(
        self,
        claim_id: str,
        file_id: str,
        doc_type: str,
        image_bytes: bytes | None,
        mime_type: str | None,
        hint: str,
    ) -> tuple[dict[str, Any], float]:
        return {}, 0.5

    def classify_document_type(
        self,
        claim_id: str,
        file_id: str,
        image_bytes: bytes,
        mime_type: str | None,
        allowed_labels: list[str],
    ) -> tuple[str | None, float]:
        return None, 0.0

    def assess_waiting_period_clinical(
        self,
        claim_id: str,
        clinical_bundle: str,
        condition_catalog: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], float]:
        return {"matches": [], "insufficient_clinical_information": True}, 0.5
