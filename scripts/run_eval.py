#!/usr/bin/env python3
"""Run 12 official fixture cases; write docs/EVAL_REPORT.md."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from claims_pipeline.config import POLICY_PATH, TEST_CASES_PATH
from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, load_policy_file


def main() -> None:
    terms = load_policy_file(POLICY_PATH)
    svc = PolicyService(terms)
    with open(TEST_CASES_PATH, encoding="utf-8") as f:
        bundle = json.load(f)

    lines: list[str] = []
    lines.append(f"# EVAL_REPORT (fixture, no LLM)\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n")
    for case in bundle["test_cases"]:
        cid = case["case_id"]
        ctx = run_pipeline_sync(case["input"], terms, 1, svc, llm_provider=None)
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


if __name__ == "__main__":
    main()
