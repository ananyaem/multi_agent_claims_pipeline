"""Load prior Claim rows from fixtures/eval_db_seeds.json for eval and tests (idempotent by claim_id)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from claims_pipeline.config import EVAL_DB_SEEDS_PATH
from claims_pipeline.db import Claim
from claims_pipeline.policy import get_active_policy_terms


def _load_case_seeds(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    p = path or EVAL_DB_SEEDS_PATH
    if not p.is_file():
        return {}
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    raw = data.get("case_seeds") or {}
    return {str(k): v for k, v in raw.items() if isinstance(v, list)}


def _entry_to_claim_row(db: Session, entry: dict[str, Any]) -> Claim | None:
    claim_id = str(entry.get("claim_id") or "").strip()
    if not claim_id:
        return None
    if db.query(Claim).filter(Claim.claim_id == claim_id).first():
        return None
    member_id = str(entry.get("member_id") or "").strip()
    treatment_date = str(entry.get("treatment_date") or "").strip()[:32]
    category = str(entry.get("category") or "CONSULTATION").strip()
    try:
        claimed = float(entry.get("claimed_amount", 0))
    except (TypeError, ValueError):
        claimed = 0.0
    pv_id, _ = get_active_policy_terms(db)
    hosp = entry.get("hospital_name")
    sub: dict[str, Any] = {
        "member_id": member_id,
        "claim_category": category,
    }
    if hosp:
        sub["hospital_name"] = str(hosp)
    status = str(entry.get("status") or "DONE")
    decision = entry.get("decision")
    if decision is not None:
        decision = str(decision)
    else:
        decision = "APPROVED"
    return Claim(
        claim_id=claim_id,
        member_id=member_id,
        policy_version_id=pv_id,
        category=category,
        claimed_amount=claimed,
        treatment_date=treatment_date,
        submission=sub,
        status=status,
        decision=decision,
    )


def seed_eval_prior_claims_for_case(
    db: Session,
    case_id: str,
    *,
    seeds_path: Path | None = None,
) -> int:
    """Insert prior claims declared for this case_id in eval_db_seeds.json. Returns rows inserted."""
    case_seeds = _load_case_seeds(seeds_path)
    entries = case_seeds.get(case_id) or []
    n = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        row = _entry_to_claim_row(db, entry)
        if row is None:
            continue
        db.add(row)
        n += 1
    if n:
        db.commit()
    return n


def seed_all_eval_prior_claims(db: Session, *, seeds_path: Path | None = None) -> int:
    """Insert every prior-claim entry from eval_db_seeds.json (all case_ids). Returns rows inserted."""
    case_seeds = _load_case_seeds(seeds_path)
    n = 0
    for entries in case_seeds.values():
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            row = _entry_to_claim_row(db, entry)
            if row is None:
                continue
            db.add(row)
            n += 1
    if n:
        db.commit()
    return n
