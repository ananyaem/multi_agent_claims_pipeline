from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from claims_pipeline.config import POLICY_PATH
from claims_pipeline.db import Member, PolicyVersion


def canonical_json_hash(obj: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def load_policy_file(path: Path | None = None) -> dict[str, Any]:
    p = path or POLICY_PATH
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def seed_policy_and_members(db: Session, policy_path: Path | None = None) -> int:
    """Insert policy version if hash missing; upsert members from policy. Returns active policy_version id."""
    terms = load_policy_file(policy_path)
    h = canonical_json_hash(terms)
    existing = db.query(PolicyVersion).filter(PolicyVersion.content_hash == h).first()
    if existing:
        pv_id = existing.id
        # ensure active
        if not existing.is_active:
            db.query(PolicyVersion).update({PolicyVersion.is_active: False})
            existing.is_active = True
            db.commit()
    else:
        db.query(PolicyVersion).update({PolicyVersion.is_active: False})
        pv = PolicyVersion(policy_id=terms["policy_id"], content_hash=h, terms=terms, is_active=True)
        db.add(pv)
        db.commit()
        db.refresh(pv)
        pv_id = pv.id

    for m in terms.get("members", []):
        mid = m["member_id"]
        row = db.query(Member).filter(Member.member_id == mid).first()
        if row:
            row.name = m.get("name", "")
            row.join_date = m.get("join_date")
            row.raw = m
        else:
            db.add(
                Member(
                    member_id=mid,
                    name=m.get("name", ""),
                    join_date=m.get("join_date"),
                    raw=m,
                )
            )
    db.commit()
    return pv_id


def get_active_policy_terms(db: Session) -> tuple[int, dict[str, Any]]:
    pv = db.query(PolicyVersion).filter(PolicyVersion.is_active == True).first()  # noqa: E712
    if not pv:
        seed_policy_and_members(db)
        pv = db.query(PolicyVersion).filter(PolicyVersion.is_active == True).first()  # noqa: E712
    return pv.id, pv.terms


class PolicyService:
    """In-memory view of active policy for runtime."""

    def __init__(self, terms: dict[str, Any]):
        self.terms = terms

    def category_key(self, claim_category: str) -> str:
        return claim_category.lower()

    def document_requirements(self, claim_category: str) -> dict[str, list[str]]:
        key = claim_category.upper()
        req = self.terms.get("document_requirements", {}).get(key, {})
        return {"required": list(req.get("required", [])), "optional": list(req.get("optional", []))}

    def opd_category(self, claim_category: str) -> dict[str, Any]:
        ck = self.category_key(claim_category)
        return self.terms.get("opd_categories", {}).get(ck, {})

    def member_by_id(self, member_id: str) -> dict[str, Any] | None:
        for m in self.terms.get("members", []):
            if m["member_id"] == member_id:
                return m
        return None


@lru_cache
def policy_service_from_file(path: str | None = None) -> PolicyService:
    p = Path(path) if path else POLICY_PATH
    with open(p, encoding="utf-8") as f:
        terms = json.load(f)
    return PolicyService(terms)
