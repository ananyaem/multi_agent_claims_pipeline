from __future__ import annotations

from typing import Any, Protocol

from claims_pipeline.config import upload_root_path
from claims_pipeline.pipeline.context import PipelineContext


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


def run_extraction(ctx: PipelineContext, llm: LLMExtractor | None) -> None:
    """Populate extracted_documents from fixture content or LLM."""
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
        data, conf = llm.extract_document(ctx.claim_id, fid, dtype, raw_bytes, mime, "")
        meta = data.pop("_extraction_meta", None)
        clean = _strip_llm_internal_keys(data)
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
