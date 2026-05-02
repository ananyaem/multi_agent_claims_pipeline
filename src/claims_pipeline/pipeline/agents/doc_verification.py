from __future__ import annotations

from collections import Counter

from claims_pipeline.pipeline.context import PipelineContext
from claims_pipeline.policy import PolicyService


def run_document_verification(ctx: PipelineContext, policy: PolicyService) -> None:
    cat = ctx.submission["claim_category"].upper()
    reqs = policy.document_requirements(cat)
    required = reqs["required"]
    docs = ctx.submission.get("documents", [])
    uploaded_types = [d.get("actual_type") for d in docs if d.get("actual_type")]
    counts = Counter(uploaded_types)

    missing = []
    for rt in required:
        if counts.get(rt, 0) < 1:
            missing.append(rt)

    if not missing:
        ctx.add_step_confidence(0.98)
        return

    uploaded_summary = ", ".join(f"{t} ({counts[t]} file(s))" for t in counts if t)
    needed = ", ".join(required)
    ctx.halted_reason = "WRONG_DOCUMENTS"
    ctx.member_message = (
        f"Your claim is missing required documents. You uploaded: {uploaded_summary}. "
        f"This claim type requires: {needed}. "
        "Please upload the missing document type(s) — for example, a Hospital Bill is required "
        "but we only received Prescription(s)."
    )
    ctx.halt_details = {
        "uploaded_types": list(counts.keys()),
        "required_types": required,
        "missing": missing,
    }
    ctx.add_step_confidence(0.96)
