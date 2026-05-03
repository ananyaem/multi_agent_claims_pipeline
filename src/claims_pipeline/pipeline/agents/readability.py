"""Computed readability (pixels + extraction model), not UI `quality` flags."""

from __future__ import annotations

from claims_pipeline.config import get_settings
from claims_pipeline.image_quality import assess_image_bytes
from claims_pipeline.pipeline.agents.visual_classification import _load_upload_bytes
from claims_pipeline.pipeline.context import PipelineContext


def run_readability(ctx: PipelineContext) -> None:
    """
    Runs after extraction. Uses:
    - Laplacian sharpness on raw pixels (severe blur → NEEDS_REUPLOAD).
    - `_meta.readability` from the extraction LLM when present.
    - Fixture-only fallback: `quality` on a document when no file bytes exist (official JSON tests).
    """
    floor = float(get_settings().readability_hard_laplacian_floor)
    by_id = {e.get("file_id"): e for e in ctx.extracted_documents}

    for doc in ctx.submission.get("documents", []):
        fid = doc.get("file_id")
        fname = doc.get("file_name") or doc.get("file_id") or "document"
        row = by_id.get(fid)
        if row is None:
            continue

        raw, _mime = _load_upload_bytes(doc)
        meta = row.get("extraction_meta") if isinstance(row.get("extraction_meta"), dict) else {}

        if raw:
            metrics = assess_image_bytes(raw)
            row["readability_metrics"] = metrics
            v = metrics.get("laplacian_variance")
            if v is not None and v < floor:
                ctx.halted_reason = "NEEDS_REUPLOAD"
                ctx.member_message = (
                    f"We could not reliably read '{fname}'. The image looks too blurry or low-detail "
                    f"(sharpness score {v:.1f}; we need at least about {floor:.0f} for automatic processing). "
                    "Please re-upload a clearer photo or scan of this document."
                )
                ctx.halt_details = {
                    "file_id": fid,
                    "issue": "LOW_SHARPNESS",
                    "laplacian_variance": v,
                    "floor": floor,
                }
                ctx.add_step_confidence(0.85, step="ReadabilityAgent")
                return

            if meta.get("readability") == "UNREADABLE":
                ctx.halted_reason = "NEEDS_REUPLOAD"
                notes = meta.get("notes") or "The model could not read this image reliably."
                ctx.member_message = (
                    f"We could not read '{fname}' well enough to process it automatically. {notes} "
                    "Please re-upload a clearer photo or scan."
                )
                ctx.halt_details = {"file_id": fid, "issue": "MODEL_UNREADABLE", "extraction_meta": meta}
                ctx.add_step_confidence(float(meta.get("confidence", 0.55)), step="ReadabilityAgent")
                return
        else:
            # Official fixture JSON with explicit quality (no upload bytes in unit tests)
            if doc.get("quality") == "UNREADABLE":
                dtype = doc.get("actual_type", "document")
                ctx.halted_reason = "NEEDS_REUPLOAD"
                ctx.member_message = (
                    f"We could not read the file '{fname}' ({dtype}). "
                    "Please re-upload a clearer photo or scan of this document so we can process your claim."
                )
                ctx.halt_details = {"file_id": fid, "issue": "UNREADABLE", "source": "fixture_marker"}
                ctx.add_step_confidence(0.85, step="ReadabilityAgent")
                return

            if meta.get("readability") == "UNREADABLE":
                ctx.halted_reason = "NEEDS_REUPLOAD"
                notes = meta.get("notes") or ""
                ctx.member_message = (
                    f"We could not read '{fname}' well enough. {notes} "
                    "Please re-upload a clearer photo or scan."
                )
                ctx.halt_details = {"file_id": fid, "issue": "MODEL_UNREADABLE", "extraction_meta": meta}
                ctx.add_step_confidence(float(meta.get("confidence", 0.55)), step="ReadabilityAgent")
                return

    ctx.add_step_confidence(0.96, step="ReadabilityAgent")
