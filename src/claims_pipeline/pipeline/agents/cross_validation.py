from __future__ import annotations

from claims_pipeline.pipeline.context import PipelineContext


def _pick_patient_name(doc: dict) -> str | None:
    data = doc.get("data") or {}
    if doc.get("patient_name_on_doc"):
        return doc["patient_name_on_doc"]
    return data.get("patient_name")


def run_cross_validation(ctx: PipelineContext) -> None:
    """TC003: mismatch patient names across documents."""
    names: list[tuple[str, str]] = []
    for doc in ctx.extracted_documents:
        fid = doc.get("file_id", "")
        # metadata from original submission
        sub_doc = next((d for d in ctx.submission["documents"] if d.get("file_id") == fid), {})
        if sub_doc.get("patient_name_on_doc"):
            names.append((fid, sub_doc["patient_name_on_doc"]))
            continue
        n = _pick_patient_name(doc)
        if n:
            names.append((fid, n))

    if len(names) < 2:
        ctx.add_step_confidence(0.93)
        return

    normalized = [n[1].strip().lower() for n in names]
    if len(set(normalized)) > 1:
        detail_parts = [f"{fid}: {name}" for fid, name in names]
        ctx.halted_reason = "PATIENT_MISMATCH"
        ctx.member_message = (
            "The documents appear to belong to different patients. "
            f"We found these patient names: {'; '.join(detail_parts)}. "
            "Please upload documents that all relate to the same patient and match your membership."
        )
        ctx.halt_details = {"names": names}
        ctx.add_step_confidence(0.92)
        return

    ctx.add_step_confidence(0.95)
