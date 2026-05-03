from __future__ import annotations

import json
import os
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from claims_pipeline.analytics import decisions_csv, list_decision_events
from claims_pipeline.config import ROOT, TEST_CASES_PATH, get_settings, upload_root_path

from claims_pipeline.db import Claim, PolicyVersion, TraceStepORM, init_db
from claims_pipeline.meta import document_types_from_test_cases
from claims_pipeline.policy import PolicyService, canonical_json_hash, get_active_policy_terms, seed_policy_and_members
from claims_pipeline.policy_terms_validate import validate_policy_terms
from claims_pipeline.redis_support import redis_client
from claims_pipeline.schemas import KNOWN_DOCUMENT_TYPE_STRINGS, ClaimSubmission


def _workers_health(rc, settings) -> dict[str, dict]:
    """Queue depths + heartbeat keys written by claim_worker / llm_worker."""
    now = time.time()
    out: dict[str, dict] = {}

    def _one(worker_key: str, queue_name: str, label: str) -> None:
        raw = rc.get(f"worker:heartbeat:{worker_key}")
        last: float | None = None
        alive = False
        if raw:
            try:
                s = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
                last = float(s)
                alive = (now - last) < 50.0
            except (ValueError, TypeError):
                pass
        try:
            depth = int(rc.llen(queue_name))
        except Exception:
            depth = -1
        out[label] = {
            "queue": queue_name,
            "queue_depth": depth,
            "alive": alive,
            "last_heartbeat_age_sec": None if last is None else round(now - last, 1),
        }

    _one("claim", settings.claims_queue, "claim_worker")
    _one("llm", settings.llm_queue, "llm_worker")
    return out


ROOT_DIR = ROOT


def _safe_filename(name: str | None) -> str:
    base = os.path.basename(name or "upload.bin")
    return base.replace("..", "_").strip() or "upload.bin"


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
    settings = get_settings()
    r_ok = True
    rc = None
    try:
        rc = redis_client()
        rc.ping()
    except Exception:
        r_ok = False
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    workers: dict[str, dict] | None = None
    if r_ok and rc is not None:
        try:
            workers = _workers_health(rc, settings)
        except Exception:
            workers = None

    return {
        "status": "ok",
        "redis": r_ok,
        "database": db_ok,
        "limits": {
            "max_upload_bytes": settings.max_upload_bytes,
            "max_upload_mib": round(settings.max_upload_bytes / (1024 * 1024), 2),
        },
        "workers": workers,
    }


@app.get("/policy/active")
def policy_active(db: Session = Depends(get_db)):
    pv_id, terms = get_active_policy_terms(db)
    return {"policy_version_id": pv_id, "terms": terms}


@app.get("/meta/document-types")
def meta_document_types():
    """Fixture-derived types plus OTHERS (uncategorized / manual review)."""
    merged = set(document_types_from_test_cases()) | {"OTHERS"}
    return {"document_types": sorted(merged)}


@app.get("/meta/policy-ids")
def meta_policy_ids(db: Session = Depends(get_db)):
    """Distinct `policy_id` values present in `policy_versions` (all stored versions)."""
    tuples = db.query(PolicyVersion.policy_id).distinct().all()
    ids = sorted({t[0] for t in tuples if t[0]})
    return {"policy_ids": ids}


@app.get("/meta/claim-categories")
def meta_claim_categories(db: Session = Depends(get_db)):
    """Claim categories are exactly the keys under active policy `document_requirements`."""
    _, terms = get_active_policy_terms(db)
    dr = terms.get("document_requirements") or {}
    return {"claim_categories": sorted(dr.keys())}


@app.get("/meta/document-requirements/{category}")
def meta_document_requirements(category: str, db: Session = Depends(get_db)):
    """Which document upload slots apply to this category: active policy `required` / `optional`."""
    _, terms = get_active_policy_terms(db)
    svc = PolicyService(terms)
    cat = category.strip().upper()
    if cat not in terms.get("document_requirements", {}):
        raise HTTPException(404, "unknown claim category for active policy")
    req = svc.document_requirements(cat)
    return {"claim_category": cat, "required": req["required"], "optional": req["optional"]}


@app.get("/policy/versions")
def policy_versions(db: Session = Depends(get_db)):
    rows = db.query(PolicyVersion).order_by(PolicyVersion.id.desc()).all()
    return [{"id": r.id, "policy_id": r.policy_id, "content_hash": r.content_hash, "is_active": r.is_active, "created_at": str(r.created_at)} for r in rows]


class PolicyUpload(BaseModel):
    terms: dict[str, Any]


@app.post("/admin/policy")
def admin_policy(body: PolicyUpload, db: Session = Depends(get_db)):
    errs = validate_policy_terms(body.terms)
    if errs:
        raise HTTPException(422, detail={"errors": errs})
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


@app.post("/claims/submit")
async def create_claim_with_uploads(request: Request, db: Session = Depends(get_db)):
    """Submit a claim with multipart file fields `docfile_<DOCUMENT_TYPE>` (repeatable per type)."""
    form = await request.form()

    def field_str(name: str) -> str | None:
        v = form.get(name)
        if v is None:
            return None
        if hasattr(v, "read"):
            return None
        s = str(v).strip()
        return s if s else None

    member_id = field_str("member_id")
    policy_id = field_str("policy_id")
    claim_category = field_str("claim_category")
    treatment_date = field_str("treatment_date") or ""
    hospital_name = field_str("hospital_name")

    try:
        claimed_amount = float(field_str("claimed_amount") or "0")
    except ValueError:
        raise HTTPException(422, "claimed_amount must be a number")
    ytd_raw = field_str("ytd_claims_amount")
    ytd_claims_amount: float | None = None
    if ytd_raw is not None:
        try:
            ytd_claims_amount = float(ytd_raw)
        except ValueError:
            raise HTTPException(422, "ytd_claims_amount must be a number")

    if not member_id or not policy_id or not claim_category:
        raise HTTPException(422, "member_id, policy_id, and claim_category are required")

    pv_id, terms = get_active_policy_terms(db)
    svc = PolicyService(terms)
    cat_u = claim_category.strip().upper()
    if cat_u not in terms.get("document_requirements", {}):
        raise HTTPException(422, f"claim_category {cat_u} is not configured on the active policy")

    reqs = svc.document_requirements(cat_u)
    policy_slots = set(reqs["required"]) | set(reqs["optional"])
    # Allow any known document type as an extra attachment (manual review / classification later).
    extra_allow = set(KNOWN_DOCUMENT_TYPE_STRINGS) | set(document_types_from_test_cases())
    allowed = policy_slots | extra_allow

    files_by_type: defaultdict[str, list[Any]] = defaultdict(list)
    for key, val in form.multi_items():
        if isinstance(key, str) and key.startswith("docfile_") and hasattr(val, "read"):
            dt = key.removeprefix("docfile_")
            files_by_type[dt].append(val)

    for dt in files_by_type:
        if dt not in allowed:
            raise HTTPException(422, f"Unexpected docfile_{dt}: unknown document type for this submission")

    for rt in reqs["required"]:
        if not files_by_type.get(rt):
            raise HTTPException(422, f"Missing required upload for document type {rt}")

    if cat_u == "OTHERS" and not files_by_type:
        raise HTTPException(422, "OTHERS category claims require at least one uploaded document")

    claim_id = str(uuid.uuid4())
    root = upload_root_path()
    root.mkdir(parents=True, exist_ok=True)
    (root / claim_id).mkdir(parents=True, exist_ok=True)

    max_b = get_settings().max_upload_bytes
    documents: list[dict[str, Any]] = []
    for dtype, uploads in files_by_type.items():
        for uf in uploads:
            fid = str(uuid.uuid4())
            safe = _safe_filename(getattr(uf, "filename", None))
            rel = f"{claim_id}/{fid}_{safe}"
            dest = root / rel
            body_bytes = await uf.read()
            if len(body_bytes) > max_b:
                raise HTTPException(413, f"file too large for {dtype}")
            dest.write_bytes(body_bytes)
            documents.append(
                {
                    "file_id": fid,
                    "file_name": safe,
                    "actual_type": dtype,
                    "storage_relpath": rel,
                    "mime_type": getattr(uf, "content_type", None),
                }
            )

    sub: dict[str, Any] = {
        "claim_id": claim_id,
        "member_id": member_id,
        "policy_id": policy_id,
        "claim_category": cat_u,
        "treatment_date": treatment_date,
        "claimed_amount": claimed_amount,
        "documents": documents,
        "hospital_name": hospital_name,
        "ytd_claims_amount": ytd_claims_amount,
    }

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
        "pipeline_details": row.pipeline_details or {},
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

    with open(TEST_CASES_PATH, encoding="utf-8") as f:
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
    """Placeholder when document fixtures not generated yet."""
    fixtures_root = ROOT_DIR / "fixtures"
    legacy_docs = fixtures_root / "docs"
    has_per_case = (
        fixtures_root.is_dir()
        and any(
            p.is_dir() and p.name.startswith("TC") and any(p.iterdir())
            for p in fixtures_root.iterdir()
        )
    )
    has_legacy = legacy_docs.is_dir() and any(legacy_docs.iterdir())
    if not (has_per_case or has_legacy):
        return {
            "status": "skipped",
            "reason": "fixtures/TC* not present (or legacy fixtures/docs) — run scripts/gen_sample_docs.py",
        }
    return {"status": "not_implemented_in_api", "hint": "run scripts/run_robustness_eval.py"}
