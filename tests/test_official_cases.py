import copy
import json

import pytest

from claims_pipeline.eval_db_seed import seed_eval_prior_claims_for_case
from claims_pipeline.config import POLICY_PATH, TEST_CASES_PATH
from claims_pipeline.db import init_db
from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, get_active_policy_terms, load_policy_file, seed_policy_and_members

with open(TEST_CASES_PATH, encoding="utf-8") as f:
    CASES = {c["case_id"]: c for c in json.load(f)["test_cases"]}


@pytest.fixture
def policy_terms():
    return load_policy_file(POLICY_PATH)


@pytest.fixture
def policy_svc(policy_terms):
    return PolicyService(policy_terms)


def test_tc001_wrong_docs(policy_terms, policy_svc):
    c = CASES["TC001"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.halted_reason == "WRONG_DOCUMENTS"
    assert "PRESCRIPTION" in ctx.member_message or "prescription" in ctx.member_message.lower()
    assert "HOSPITAL_BILL" in ctx.member_message or "hospital" in ctx.member_message.lower()


def test_tc002_unreadable(policy_terms, policy_svc):
    c = CASES["TC002"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.halted_reason == "NEEDS_REUPLOAD"
    assert "blurry_bill" in ctx.member_message or "re-upload" in ctx.member_message.lower()


def test_tc003_patient_mismatch(policy_terms, policy_svc):
    c = CASES["TC003"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.halted_reason == "PATIENT_MISMATCH"
    assert "Rajesh" in ctx.member_message and "Arjun" in ctx.member_message


def test_tc004_clean_consultation(policy_terms, policy_svc):
    c = CASES["TC004"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "APPROVED"
    assert ctx.approved_amount == 1350
    assert ctx.confidence is not None and ctx.confidence > 0.85


def test_tc005_waiting_period(policy_terms, policy_svc):
    c = CASES["TC005"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "REJECTED"
    assert "WAITING_PERIOD" in ctx.rejection_reasons


def test_tc006_dental_partial(policy_terms, policy_svc):
    c = CASES["TC006"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "PARTIAL"
    assert ctx.approved_amount == 8000
    msg = (ctx.member_message or "").lower()
    assert "root canal" in msg and "teeth whitening" in msg
    assert "covered" in msg and ("not covered" in msg or "excluded" in msg or "cosmetic" in msg)


def test_tc007_pre_auth(policy_terms, policy_svc):
    c = CASES["TC007"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "REJECTED"
    assert "PRE_AUTH_MISSING" in ctx.rejection_reasons


def test_tc008_per_claim(policy_terms, policy_svc):
    c = CASES["TC008"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "REJECTED"
    assert "PER_CLAIM_EXCEEDED" in ctx.rejection_reasons


def test_tc009_fraud_manual(tmp_path):
    """Fraud uses DB-backed same-day history (not submission payload)."""
    db_url = f"sqlite:///{tmp_path / 'tc009.db'}"
    init_db(db_url)
    from claims_pipeline.db import SessionLocal

    db = SessionLocal()
    try:
        seed_policy_and_members(db)
        pv_id, terms = get_active_policy_terms(db)
        seed_eval_prior_claims_for_case(db, "TC009")
        sub = copy.deepcopy(CASES["TC009"]["input"])
        sub.pop("claims_history", None)
        sub["claim_id"] = "CLM_PYTEST_TC009_CURRENT"
        ctx = run_pipeline_sync(
            sub,
            terms,
            pv_id,
            PolicyService(terms),
            llm_provider=None,
            claim_id="CLM_PYTEST_TC009_CURRENT",
            db=db,
        )
        assert ctx.decision == "MANUAL_REVIEW"
    finally:
        db.close()


def test_tc010_network_discount(policy_terms, policy_svc):
    c = CASES["TC010"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "APPROVED"
    assert ctx.approved_amount == 3240
    msg = ctx.member_message or ""
    assert "₹3,240.00" in msg or "3240" in msg.replace(",", "")
    assert "network hospital" in msg.lower() and "20%" in msg and "10%" in msg
    assert "4,500.00" in msg or "4500" in msg.replace(",", "")


def test_tc011_degraded(policy_terms, policy_svc):
    c = CASES["TC011"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "APPROVED"
    assert ctx.approved_amount == 4000
    assert "FraudAgent" in ctx.degraded_components
    assert ctx.confidence is not None and ctx.confidence < 0.92


def test_tc012_excluded(policy_terms, policy_svc):
    c = CASES["TC012"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "REJECTED"
    assert "EXCLUDED_CONDITION" in ctx.rejection_reasons
