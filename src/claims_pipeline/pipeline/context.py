from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineContext:
    claim_id: str
    policy_version_id: int
    policy_terms: dict[str, Any]
    submission: dict[str, Any]  # raw input dict

    member: dict[str, Any] | None = None
    category_key: str = ""
    extracted_documents: list[dict[str, Any]] = field(default_factory=list)

    policy_findings: list[str] = field(default_factory=list)
    fraud_signals: list[str] = field(default_factory=list)
    fraud_score: float = 0.0

    decision: str | None = None
    approved_amount: float | None = None
    rejection_reasons: list[str] = field(default_factory=list)
    financial_breakdown: dict[str, Any] = field(default_factory=dict)
    member_message: str | None = None

    halted_reason: str | None = None  # WRONG_DOCUMENTS, NEEDS_REUPLOAD, PATIENT_MISMATCH, ...
    halt_details: dict[str, Any] = field(default_factory=dict)

    degraded_components: list[str] = field(default_factory=list)
    simulate_component_failure: bool = False

    network_hospital: bool = False
    hospital_name_for_network: str | None = None

    # Named step scores for harmonic headline confidence + API breakdown
    step_confidence_records: list[tuple[str, float]] = field(default_factory=list)
    confidence: float | None = None  # headline harmonic aggregate
    confidence_breakdown: dict[str, Any] = field(default_factory=dict)
    pipeline_details: dict[str, Any] = field(default_factory=dict)

    def add_step_confidence(self, c: float, *, step: str = "pipeline") -> None:
        self.step_confidence_records.append((step, max(0.0, min(1.0, c))))
