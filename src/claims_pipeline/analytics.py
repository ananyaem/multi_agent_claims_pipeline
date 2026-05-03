from __future__ import annotations

import csv
import io
from typing import Any

from sqlalchemy.orm import Session

from claims_pipeline.db import DecisionEvent


def list_decision_events(db: Session, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    rows = (
        db.query(DecisionEvent)
        .order_by(DecisionEvent.decided_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    out = []
    for r in rows:
        out.append(
            {
                "claim_id": r.claim_id,
                "member_id": r.member_id,
                "category": r.category,
                "claimed_amount": r.claimed_amount,
                "approved_amount": r.approved_amount,
                "decision": r.decision,
                "rejection_reasons": r.rejection_reasons,
                "confidence": r.confidence,
                "policy_version_id": r.policy_version_id,
                "hospital_name": r.hospital_name,
                "is_network_hospital": r.is_network_hospital,
                "decided_at": r.decided_at.isoformat() if r.decided_at else None,
            }
        )
    return out


def decisions_csv(db: Session) -> str:
    buf = io.StringIO()
    rows = db.query(DecisionEvent).order_by(DecisionEvent.decided_at.desc()).all()
    if not rows:
        return ""
    w = csv.writer(buf)
    w.writerow(
        [
            "claim_id",
            "member_id",
            "category",
            "claimed_amount",
            "approved_amount",
            "decision",
            "confidence",
            "policy_version_id",
            "decided_at",
        ]
    )
    for r in rows:
        w.writerow(
            [
                r.claim_id,
                r.member_id,
                r.category,
                r.claimed_amount,
                r.approved_amount,
                r.decision,
                r.confidence,
                r.policy_version_id,
                r.decided_at.isoformat() if r.decided_at else "",
            ]
        )
    return buf.getvalue()
