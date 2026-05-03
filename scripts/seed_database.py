#!/usr/bin/env python3
"""One-shot database seed: policy + members (from assignment/policy_terms.json) and prior-claim eval fixtures (fixtures/eval_db_seeds.json)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from claims_pipeline.config import get_settings
from claims_pipeline.db import init_db
from claims_pipeline.eval_db_seed import seed_all_eval_prior_claims
from claims_pipeline.policy import seed_policy_and_members


def main() -> int:
    settings = get_settings()
    init_db(settings.database_url)
    import claims_pipeline.db as db_mod

    db = db_mod.SessionLocal()
    try:
        seed_policy_and_members(db)
        n = seed_all_eval_prior_claims(db)
        print(f"Seeded active policy and members. Inserted {n} prior-claim row(s) from fixtures/eval_db_seeds.json.")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
