from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


DocumentType = Literal[
    "PRESCRIPTION",
    "HOSPITAL_BILL",
    "LAB_REPORT",
    "PHARMACY_BILL",
    "DISCHARGE_SUMMARY",
    "DIAGNOSTIC_REPORT",
    "DENTAL_REPORT",
]


class DocumentInput(BaseModel):
    file_id: str
    file_name: str | None = None
    actual_type: str | None = None
    quality: str | None = None  # GOOD | UNREADABLE
    patient_name_on_doc: str | None = None
    content: dict[str, Any] | None = None


class ClaimSubmission(BaseModel):
    member_id: str
    policy_id: str
    claim_category: str
    treatment_date: str
    claimed_amount: float
    documents: list[DocumentInput]
    ytd_claims_amount: float | None = None
    hospital_name: str | None = None
    claims_history: list[dict[str, Any]] | None = None
    simulate_component_failure: bool | None = None


class TraceStepOut(BaseModel):
    seq: int
    stage: str
    status: str
    findings: list[str] | dict[str, Any] = Field(default_factory=list)
    duration_ms: int | None = None
    confidence: float | None = None


class LLMCallOut(BaseModel):
    stage: str
    model: str
    tokens_in: int | None = None
    tokens_out: int | None = None
    latency_ms: int | None = None
    parse_status: str | None = None


class ClaimDecision(BaseModel):
    decision: str | None = None  # APPROVED | PARTIAL | REJECTED | MANUAL_REVIEW | NEEDS_USER_ACTION
    approved_amount: float | None = None
    confidence: float | None = None
    member_message: str | None = None
    rejection_reasons: list[str] | None = None
    financial_breakdown: dict[str, Any] | None = None
    degraded_components: list[str] = Field(default_factory=list)
    halted_reason: str | None = None
    trace_steps: list[TraceStepOut] = Field(default_factory=list)
    llm_calls: list[LLMCallOut] = Field(default_factory=list)


class EvalCaseResult(BaseModel):
    case_id: str
    passed: bool
    notes: str = ""
