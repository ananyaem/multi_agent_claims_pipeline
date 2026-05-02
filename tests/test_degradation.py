"""TC011 degradation path — FraudAgent penalty lowers harmonic confidence."""

import json
from pathlib import Path

from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, load_policy_file

ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / "test_cases.json", encoding="utf-8") as f:
    TC011 = next(c for c in json.load(f)["test_cases"] if c["case_id"] == "TC011")


def test_tc011_simulated_failure_lowers_confidence():
    terms = load_policy_file(ROOT / "policy_terms.json")
    svc = PolicyService(terms)
    ctx = run_pipeline_sync(TC011["input"], terms, 1, svc, None)
    assert "FraudAgent" in ctx.degraded_components
    assert ctx.decision == "APPROVED"
    assert ctx.confidence is not None and ctx.confidence < 0.92
