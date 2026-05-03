"""First-step vision classifier: compare Gemini label vs declared slot type before intake."""

from __future__ import annotations

from typing import Any

from claims_pipeline.config import upload_root_path
from claims_pipeline.llm.image_compress import compress_for_llm_vision
from claims_pipeline.pipeline.context import PipelineContext
from claims_pipeline.schemas import KNOWN_DOCUMENT_TYPE_STRINGS


_PRETTY = {
    "PRESCRIPTION": "a Prescription",
    "HOSPITAL_BILL": "a Hospital Bill",
    "LAB_REPORT": "a Lab Report",
    "PHARMACY_BILL": "a Pharmacy Bill",
    "DISCHARGE_SUMMARY": "a Discharge Summary",
    "DIAGNOSTIC_REPORT": "a Diagnostic Report",
    "DENTAL_REPORT": "a Dental Report",
    "OTHERS": "an Other / uncategorized document",
}


def _pretty(token: str | None) -> str:
    if not token:
        return "something we could not categorize"
    return _PRETTY.get(token.upper(), token.replace("_", " ").lower())


def _load_upload_bytes(doc: dict[str, Any]) -> tuple[bytes | None, str | None]:
    rel = doc.get("storage_relpath")
    if not rel:
        return None, doc.get("mime_type")
    root = upload_root_path()
    path = root / rel
    try:
        if path.is_file() and path.resolve().is_relative_to(root.resolve()):
            return path.read_bytes(), doc.get("mime_type")
    except (OSError, ValueError):
        pass
    return None, doc.get("mime_type")


def run_visual_document_classification(ctx: PipelineContext, llm: Any | None) -> None:
    """
    For each uploaded image, classify with Gemini and ensure the declared upload slot
    matches what the image shows. Updates submission actual_type to the visual label on success.
    Skips documents that include embedded fixture `content` (unit tests) or have no file bytes.
    """
    if llm is None:
        ctx.add_step_confidence(1.0, step="VisualDocumentClassificationAgent")
        return

    docs = ctx.submission.get("documents") or []
    allowed = sorted(KNOWN_DOCUMENT_TYPE_STRINGS)

    confidences: list[float] = []
    degraded = False
    for doc in docs:
        if doc.get("content") is not None:
            continue
        raw, mime = _load_upload_bytes(doc)
        if not raw:
            continue

        fid = str(doc.get("file_id", ""))
        fname = doc.get("file_name") or fid
        comp_bytes, comp_mime = compress_for_llm_vision(raw, mime)

        try:
            visual, conf = llm.classify_document_type(
                ctx.claim_id,
                fid,
                comp_bytes,
                comp_mime,
                allowed,
            )
        except Exception:
            degraded = True
            continue

        if visual is None:
            degraded = True
            continue

        confidences.append(conf)
        declared = (doc.get("actual_type") or "").strip().upper()
        if declared and declared != visual:
            ctx.halted_reason = "DOCUMENT_TYPE_MISMATCH"
            ctx.member_message = (
                f"“{fname}” was submitted as {_pretty(declared)}, but the image looks like {_pretty(visual)}. "
                "Please pick the correct document type for that file, or upload a different document."
            )
            ctx.halt_details = {
                "file_id": fid,
                "file_name": fname,
                "declared_type": declared,
                "visual_type": visual,
                "confidence": conf,
            }
            ctx.add_step_confidence(conf, step="VisualDocumentClassificationAgent")
            return

        doc["actual_type"] = visual
        doc["visual_document_type"] = visual
        doc["visual_classification_confidence"] = conf

    if degraded:
        ctx.degraded_components.append("VisualClassificationAgent")
    if confidences:
        ctx.add_step_confidence(
            sum(confidences) / len(confidences),
            step="VisualDocumentClassificationAgent",
        )
    elif degraded:
        ctx.add_step_confidence(0.72, step="VisualDocumentClassificationAgent")
    else:
        ctx.add_step_confidence(1.0, step="VisualDocumentClassificationAgent")
