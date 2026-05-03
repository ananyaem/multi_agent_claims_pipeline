from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from claims_pipeline.analytics import decisions_csv, list_decision_events
from claims_pipeline.config import ROOT, get_settings

from claims_pipeline.db import Claim, PolicyVersion, TraceStepORM, init_db
from claims_pipeline.policy import canonical_json_hash, get_active_policy_terms, seed_policy_and_members
from claims_pipeline.queue import redis_client
from claims_pipeline.schemas import ClaimSubmission

ROOT_DIR = ROOT


def get_db():
    from claims_pipeline.db import SessionLocal

    if SessionLocal is None:
        init_db(get_settings().database_url)
    from claims_pipeline.db import SessionLocal as SL

    db = SL()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(get_settings().database_url)
    db = next(get_db())
    try:
        seed_policy_and_members(db)
        db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="Claims Pipeline API", lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    r_ok = True
    try:
        redis_client().ping()
    except Exception:
        r_ok = False
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return {"status": "ok", "redis": r_ok, "database": db_ok}


@app.get("/policy/active")
def policy_active(db: Session = Depends(get_db)):
    pv_id, terms = get_active_policy_terms(db)
    return {"policy_version_id": pv_id, "terms": terms}


@app.get("/policy/versions")
def policy_versions(db: Session = Depends(get_db)):
    rows = db.query(PolicyVersion).order_by(PolicyVersion.id.desc()).all()
    return [{"id": r.id, "policy_id": r.policy_id, "content_hash": r.content_hash, "is_active": r.is_active, "created_at": str(r.created_at)} for r in rows]


class PolicyUpload(BaseModel):
    terms: dict[str, Any]


@app.post("/admin/policy")
def admin_policy(body: PolicyUpload, db: Session = Depends(get_db)):
    h = canonical_json_hash(body.terms)
    for row in db.query(PolicyVersion).all():
        row.is_active = False
    existing = db.query(PolicyVersion).filter(PolicyVersion.content_hash == h).first()
    if existing:
        existing.is_active = True
        db.commit()
        return {"policy_version_id": existing.id, "content_hash": h, "status": "reactivated"}
    pv = PolicyVersion(policy_id=body.terms.get("policy_id", "UNKNOWN"), content_hash=h, terms=body.terms, is_active=True)
    db.add(pv)
    db.commit()
    db.refresh(pv)
    return {"policy_version_id": pv.id, "content_hash": h, "status": "created"}


@app.post("/claims")
def create_claim(body: ClaimSubmission, db: Session = Depends(get_db)):
    pv_id, terms = get_active_policy_terms(db)
    claim_id = str(uuid.uuid4())
    sub = body.model_dump()
    sub["claim_id"] = claim_id
    db.add(
        Claim(
            claim_id=claim_id,
            member_id=sub["member_id"],
            policy_version_id=pv_id,
            category=sub["claim_category"],
            claimed_amount=float(sub["claimed_amount"]),
            treatment_date=sub["treatment_date"],
            submission=sub,
            status="PENDING",
        )
    )
    db.commit()
    r = redis_client()
    r.rpush(get_settings().claims_queue, json.dumps({"claim_id": claim_id, "submission": sub}))
    return {"claim_id": claim_id, "status": "queued"}


@app.get("/claims/{claim_id}")
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    row = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not row:
        raise HTTPException(404, "claim not found")
    trace = db.query(TraceStepORM).filter(TraceStepORM.claim_id == claim_id).order_by(TraceStepORM.seq).all()
    return {
        "claim_id": row.claim_id,
        "status": row.status,
        "decision": row.decision,
        "approved_amount": row.approved_amount,
        "confidence": row.confidence,
        "member_message": row.member_message,
        "financial_breakdown": row.financial_breakdown,
        "degraded_components": row.degraded_components,
        "halted_reason": row.halted_reason,
        "rejection_reasons": row.rejection_reasons,
        "submission": row.submission,
        "trace_steps": [
            {
                "seq": t.seq,
                "stage": t.stage,
                "status": t.status,
                "findings": t.findings,
                "confidence": t.confidence,
            }
            for t in trace
        ],
    }


@app.get("/claims")
def list_claims(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(Claim).order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "claim_id": r.claim_id,
            "member_id": r.member_id,
            "status": r.status,
            "decision": r.decision,
            "claimed_amount": r.claimed_amount,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@app.get("/analytics/decisions")
def analytics_decisions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_decision_events(db, skip, limit)


@app.get("/analytics/decisions.csv")
def analytics_csv(db: Session = Depends(get_db)):
    return PlainTextResponse(decisions_csv(db), media_type="text/csv")


@app.post("/eval/run")
def eval_run(db: Session = Depends(get_db)):
    from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
    from claims_pipeline.policy import PolicyService

    path = ROOT_DIR / "test_cases.json"
    with open(path, encoding="utf-8") as f:
        bundle = json.load(f)
    pv_id, terms = get_active_policy_terms(db)
    svc = PolicyService(terms)
    results = []
    for case in bundle["test_cases"]:
        cid = case["case_id"]
        ctx = run_pipeline_sync(case["input"], terms, pv_id, svc, llm_provider=None)
        results.append(
            {
                "case_id": cid,
                "halted": ctx.halted_reason,
                "decision": ctx.decision,
                "approved_amount": ctx.approved_amount,
                "confidence": ctx.confidence,
            }
        )
    return {"results": results, "count": len(results)}


@app.post("/eval/robustness")
def eval_robustness(db: Session = Depends(get_db)):
    """Placeholder when fixtures/docs not generated yet."""
    fixtures = ROOT_DIR / "fixtures" / "docs"
    if not fixtures.exists():
        return {"status": "skipped", "reason": "fixtures/docs not present — run scripts/gen_sample_docs.py"}
    return {"status": "not_implemented_in_api", "hint": "run scripts/run_robustness_eval.py"}
