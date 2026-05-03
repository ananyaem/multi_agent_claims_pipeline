"""BLPOP claims:queue — load claim, run pipeline with RedisLLMProvider, persist."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session

from claims_pipeline.config import get_settings
from claims_pipeline.db import Claim, DecisionEvent, init_db
from claims_pipeline.llm.redis_provider import RedisLLMProvider
from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, get_active_policy_terms, seed_policy_and_members
from claims_pipeline.redis_support import redis_client, start_worker_heartbeat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def persist_result(db: Session, ctx, submission: dict) -> None:
    claim = db.query(Claim).filter(Claim.claim_id == ctx.claim_id).first()
    if not claim:
        return
    claim.status = "DONE" if not ctx.halted_reason else "HALTED"
    claim.decision = ctx.decision or ("NEEDS_USER_ACTION" if ctx.halted_reason else None)
    claim.approved_amount = ctx.approved_amount
    claim.confidence = ctx.confidence
    claim.degraded_components = ctx.degraded_components
    claim.member_message = ctx.member_message
    claim.financial_breakdown = ctx.financial_breakdown or {}
    claim.halted_reason = ctx.halted_reason
    claim.rejection_reasons = ctx.rejection_reasons
    db.add(
        DecisionEvent(
            claim_id=ctx.claim_id,
            member_id=submission.get("member_id", ""),
            category=submission.get("claim_category", ""),
            claimed_amount=float(submission.get("claimed_amount", 0)),
            approved_amount=ctx.approved_amount,
            decision=claim.decision,
            rejection_reasons=ctx.rejection_reasons,
            confidence=ctx.confidence,
            policy_version_id=ctx.policy_version_id,
            hospital_name=submission.get("hospital_name"),
            is_network_hospital=ctx.network_hospital,
        )
    )
    db.commit()


def main() -> None:
    settings = get_settings()
    init_db(settings.database_url)
    from claims_pipeline.db import SessionLocal

    r = redis_client()
    start_worker_heartbeat(r, "claim")
    llm = RedisLLMProvider(r)

    logger.info("Claim worker on %s", settings.claims_queue)
    while True:
        item = r.blpop(settings.claims_queue, timeout=0)
        if item is None:
            continue
        _, raw = item
        job = json.loads(raw.decode("utf-8"))
        claim_id = job["claim_id"]
        db: Session = SessionLocal()
        try:
            seed_policy_and_members(db)
            pv_id, terms = get_active_policy_terms(db)
            svc = PolicyService(terms)
            submission = job["submission"]
            ctx = run_pipeline_sync(
                submission,
                terms,
                pv_id,
                svc,
                llm_provider=llm,
                trace=None,
                claim_id=claim_id,
            )
            persist_result(db, ctx, submission)
            logger.info("Processed claim %s decision=%s", claim_id, ctx.decision)
        finally:
            db.close()


if __name__ == "__main__":
    main()
