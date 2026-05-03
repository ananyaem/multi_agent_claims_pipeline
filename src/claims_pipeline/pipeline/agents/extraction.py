from __future__ import annotations

from typing import Any, Protocol

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


def run_extraction(ctx: PipelineContext, llm: LLMExtractor | None) -> None:
    """Populate extracted_documents from fixture content or LLM."""
    for doc in ctx.submission.get("documents", []):
        fid = doc.get("file_id", "")
        dtype = doc.get("actual_type") or "UNKNOWN"
        if doc.get("content") is not None:
            row = {
                "file_id": fid,
                "actual_type": dtype,
                "data": doc["content"],
            }
            if doc.get("patient_name_on_doc"):
                row["patient_name_on_doc"] = doc["patient_name_on_doc"]
            ctx.extracted_documents.append(row)
            ctx.add_step_confidence(0.94)
            continue
        # No structured content: require LLM path (robustness / uploaded files)
        if llm is None:
            ctx.degraded_components.append("ExtractionAgent")
            row = {"file_id": fid, "actual_type": dtype, "data": {}}
            if doc.get("patient_name_on_doc"):
                row["patient_name_on_doc"] = doc["patient_name_on_doc"]
            ctx.extracted_documents.append(row)
            ctx.add_step_confidence(0.4)
            continue
        data, conf = llm.extract_document(ctx.claim_id, fid, dtype, None, None, "")
        row = {"file_id": fid, "actual_type": dtype, "data": data}
        if doc.get("patient_name_on_doc"):
            row["patient_name_on_doc"] = doc["patient_name_on_doc"]
        ctx.extracted_documents.append(row)
        ctx.add_step_confidence(conf)
