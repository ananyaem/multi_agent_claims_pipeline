#!/usr/bin/env python3
"""Run 12 official fixture cases; write docs/EVAL_REPORT.md."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from claims_pipeline.eval_db_seed import seed_eval_prior_claims_for_case
from claims_pipeline.config import TEST_CASES_PATH
from claims_pipeline.db import init_db
from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, get_active_policy_terms, seed_policy_and_members


def main() -> None:
    import tempfile

    db_path = Path(tempfile.mkdtemp()) / "eval.db"
    init_db(f"sqlite:///{db_path}")
    from claims_pipeline.db import SessionLocal

    db = SessionLocal()
    try:
        seed_policy_and_members(db)
        pv_id, terms = get_active_policy_terms(db)
        svc = PolicyService(terms)
        with open(TEST_CASES_PATH, encoding="utf-8") as f:
            bundle = json.load(f)

        lines: list[str] = []
        lines.append(f"# EVAL_REPORT (fixture, no LLM)\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n")
        for case in bundle["test_cases"]:
            cid = case["case_id"]
            seed_eval_prior_claims_for_case(db, cid)
            ctx = run_pipeline_sync(case["input"], terms, pv_id, svc, llm_provider=None, db=db)
            lines.append(f"## {cid} — {case.get('case_name', '')}\n\n")
            lines.append("### Output\n\n")
            lines.append(
                json.dumps(
                    {
                        "halted_reason": ctx.halted_reason,
                        "decision": ctx.decision,
                        "approved_amount": ctx.approved_amount,
                        "confidence": ctx.confidence,
                        "member_message": ctx.member_message,
                        "rejection_reasons": ctx.rejection_reasons,
                        "degraded_components": ctx.degraded_components,
                    },
                    indent=2,
                )
            )
            lines.append("\n\n---\n\n")

        out = ROOT / "docs" / "EVAL_REPORT.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("".join(lines), encoding="utf-8")
        print(f"Wrote {out}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
