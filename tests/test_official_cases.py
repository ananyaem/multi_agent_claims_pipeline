import json

import pytest

from claims_pipeline.config import POLICY_PATH, TEST_CASES_PATH
from claims_pipeline.pipeline.orchestrator import run_pipeline_sync
from claims_pipeline.policy import PolicyService, load_policy_file

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


def test_tc009_fraud_manual(policy_terms, policy_svc):
    c = CASES["TC009"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "MANUAL_REVIEW"


def test_tc010_network_discount(policy_terms, policy_svc):
    c = CASES["TC010"]
    ctx = run_pipeline_sync(c["input"], policy_terms, 1, policy_svc, llm_provider=None)
    assert ctx.decision == "APPROVED"
    assert ctx.approved_amount == 3240


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
