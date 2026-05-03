"""Load same-day prior claims for fraud signals from the database (by member_id)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from claims_pipeline.db import Claim


def fetch_prior_same_day_claims_for_member(
    db: Session,
    member_id: str,
    treatment_date: str,
    exclude_claim_id: str | None,
) -> list[dict[str, Any]]:
    """Return prior submissions on the same calendar day as treatment_date (YYYY-MM-DD prefix match).

    Excludes the current claim_id when present so the worker does not count this submission.
    Shape matches legacy payload claims_history for FraudAgent.
    """
    if not member_id or not treatment_date:
        return []
    tprefix = treatment_date.strip()[:10]
    q = db.query(Claim).filter(Claim.member_id == member_id)
    if exclude_claim_id:
        q = q.filter(Claim.claim_id != exclude_claim_id)
    rows = q.order_by(Claim.created_at.asc()).all()
    out: list[dict[str, Any]] = []
    for row in rows:
        td = (row.treatment_date or "").strip()[:10]
        if td != tprefix:
            continue
        sub = row.submission if isinstance(row.submission, dict) else {}
        out.append(
            {
                "claim_id": row.claim_id,
                "date": td,
                "amount": float(row.claimed_amount),
                "provider": (sub.get("hospital_name") or sub.get("provider") or "") or "",
            }
        )
    return out


def enrich_submission_claims_history_from_db(db: Session | None, submission: dict[str, Any]) -> None:
    """Replace submission claims_history with DB-derived prior same-day claims (never trust client payload)."""
    if db is None:
        submission.pop("claims_history", None)
        return
    mid = submission.get("member_id")
    tid = submission.get("treatment_date") or ""
    cid = submission.get("claim_id")
    submission["claims_history"] = fetch_prior_same_day_claims_for_member(db, str(mid or ""), tid, cid)
