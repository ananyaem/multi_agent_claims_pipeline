import json
from pathlib import Path

import pytest

from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, load_policy_file

ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / "test_cases.json", encoding="utf-8") as f:
    TC = {c["case_id"]: c for c in json.load(f)["test_cases"]}


@pytest.fixture
def terms():
    return load_policy_file(ROOT / "policy_terms.json")


@pytest.fixture
def svc(terms):
    return PolicyService(terms)


def test_tc010_ordering(terms, svc):
    ctx = run_pipeline_sync(TC["TC010"]["input"], terms, 1, svc, None)
    fb = ctx.financial_breakdown or {}
    assert fb.get("after_network") == 3600.0
    assert ctx.approved_amount == 3240


def test_tc006_line_exclusion(terms, svc):
    ctx = run_pipeline_sync(TC["TC006"]["input"], terms, 1, svc, None)
    assert "Teeth Whitening" in str(ctx.financial_breakdown.get("rejected_lines", []))
