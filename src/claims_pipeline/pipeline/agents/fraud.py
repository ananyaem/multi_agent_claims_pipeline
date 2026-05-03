from __future__ import annotations

from claims_pipeline.pipeline.context import PipelineContext


def run_fraud(ctx: PipelineContext) -> None:
    """Rule-based fraud signals; TC009 -> MANUAL_REVIEW; TC011 simulate failure -> degraded."""
    terms = ctx.policy_terms.get("fraud_thresholds", {})
    limit_same_day = int(terms.get("same_day_claims_limit", 99))

    if ctx.simulate_component_failure:
        ctx.degraded_components.append("FraudAgent")
        ctx.fraud_signals.append("FraudAgent skipped due to simulated component failure.")
        ctx.add_step_confidence(0.5, step="FraudAgent")
        return

    # Populated server-side from DB by treatment_date + member_id (see claims_history_db).
    hist = ctx.submission.get("claims_history") or []
    tdate = ctx.submission.get("treatment_date", "")[:10]
    same_day = [c for c in hist if str(c.get("date", ""))[:10] == tdate]

    if len(same_day) >= limit_same_day:
        ctx.fraud_signals.append(
            f"Same-day claim burst: {len(same_day)} prior claim(s) on {tdate} before this submission."
        )
        ctx.fraud_score = 0.85
        ctx.add_step_confidence(0.88, step="FraudAgent")
        return

    ctx.fraud_score = 0.1
    ctx.add_step_confidence(0.91, step="FraudAgent")
