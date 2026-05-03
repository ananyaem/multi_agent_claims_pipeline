from __future__ import annotations

from claims_pipeline.pipeline.context import PipelineContext


def run_readability(ctx: PipelineContext) -> None:
    """TC002: unreadable pharmacy bill -> NEEDS_REUPLOAD, not REJECTED."""
    for doc in ctx.submission.get("documents", []):
        q = doc.get("quality")
        if q == "UNREADABLE":
            fname = doc.get("file_name") or doc.get("file_id", "document")
            dtype = doc.get("actual_type", "document")
            ctx.halted_reason = "NEEDS_REUPLOAD"
            ctx.member_message = (
                f"We could not read the file '{fname}' ({dtype}). "
                f"Please re-upload a clearer photo or scan of this document so we can process your claim."
            )
            ctx.halt_details = {"file_id": doc.get("file_id"), "issue": "UNREADABLE"}
            ctx.add_step_confidence(0.85)
            return
    ctx.add_step_confidence(0.96)
