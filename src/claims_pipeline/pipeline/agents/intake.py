from __future__ import annotations

from claims_pipeline.pipeline.context import PipelineContext
from claims_pipeline.policy import PolicyService


def run_intake(ctx: PipelineContext, policy: PolicyService) -> None:
    mid = ctx.submission["member_id"]
    member = policy.member_by_id(mid)
    if not member:
        ctx.halted_reason = "INVALID_MEMBER"
        ctx.member_message = f"Member ID {mid} was not found on this policy roster."
        return
    ctx.member = member

    cat = ctx.submission.get("claim_category", "").upper()
    if cat not in policy.terms.get("document_requirements", {}):
        ctx.halted_reason = "INVALID_CATEGORY"
        ctx.member_message = f"Claim category {cat} is not configured for this policy."
        return

    ctx.category_key = policy.category_key(ctx.submission["claim_category"])
    ctx.add_step_confidence(0.99)
