from __future__ import annotations

import asyncio
import uuid
from typing import Any

from claims_pipeline.pipeline.agents import adjudication, cross_validation, doc_verification, extraction, fraud, intake
from claims_pipeline.pipeline.agents import policy_engine as policy_engine_mod
from claims_pipeline.pipeline.agents import readability, visual_classification
from claims_pipeline.pipeline.confidence import aggregate_claim_confidence
from claims_pipeline.pipeline.context import PipelineContext
from claims_pipeline.pipeline.tracer import TraceCollector
from claims_pipeline.policy import PolicyService


def _finalize_confidence(ctx: PipelineContext) -> None:
    if ctx.confidence is None:
        ctx.confidence = aggregate_claim_confidence(ctx.step_confidences, ctx.degraded_components)


async def run_pipeline_async(
    submission: dict[str, Any],
    policy_terms: dict[str, Any],
    policy_version_id: int,
    policy_svc: PolicyService,
    llm_provider: Any | None = None,
    trace: TraceCollector | None = None,
    claim_id: str | None = None,
) -> PipelineContext:
    cid = claim_id or submission.get("claim_id") or str(uuid.uuid4())
    ctx = PipelineContext(
        claim_id=cid,
        policy_version_id=policy_version_id,
        policy_terms=policy_terms,
        submission=submission,
        simulate_component_failure=bool(submission.get("simulate_component_failure")),
    )

    def halt() -> bool:
        return ctx.halted_reason is not None

    visual_classification.run_visual_document_classification(ctx, llm_provider)
    if trace:
        trace.emit_step(
            "VisualDocumentClassificationAgent",
            "HALT" if halt() else "OK",
            [ctx.member_message or ""],
        )
    if halt():
        _finalize_confidence(ctx)
        return ctx

    intake.run_intake(ctx, policy_svc)
    if trace:
        trace.emit_step("IntakeAgent", "OK" if not halt() else "HALT", ctx.policy_findings or ["ok"])
    if halt():
        _finalize_confidence(ctx)
        return ctx

    doc_verification.run_document_verification(ctx, policy_svc)
    if trace:
        trace.emit_step(
            "DocumentVerificationAgent",
            "HALT" if halt() else "OK",
            [ctx.member_message or ""],
        )
    if halt():
        _finalize_confidence(ctx)
        return ctx

    readability.run_readability(ctx)
    if trace:
        trace.emit_step(
            "ReadabilityAgent",
            "HALT" if halt() else "OK",
            [ctx.member_message or ""],
        )
    if halt():
        _finalize_confidence(ctx)
        return ctx

    extraction.run_extraction(ctx, llm_provider)
    if trace:
        trace.emit_step("ExtractionAgent", "OK", [f"{len(ctx.extracted_documents)} docs"])

    cross_validation.run_cross_validation(ctx)
    if trace:
        trace.emit_step(
            "CrossValidationAgent",
            "HALT" if halt() else "OK",
            [ctx.member_message or ""],
        )
    if halt():
        _finalize_confidence(ctx)
        return ctx

    await asyncio.gather(
        asyncio.to_thread(policy_engine_mod.run_policy_engine, ctx),
        asyncio.to_thread(fraud.run_fraud, ctx),
    )

    if trace:
        trace.emit_step(
            "PolicyEngine",
            "OK",
            ctx.policy_findings + ctx.rejection_reasons,
        )
        trace.emit_step("FraudAgent", "OK", ctx.fraud_signals)

    adjudication.run_adjudication(ctx)
    if trace:
        trace.emit_step(
            "AdjudicationAgent",
            "OK",
            [ctx.decision or "", str(ctx.approved_amount)],
        )

    _finalize_confidence(ctx)
    return ctx


def run_pipeline_sync(
    submission: dict[str, Any],
    policy_terms: dict[str, Any],
    policy_version_id: int,
    policy_svc: PolicyService,
    llm_provider: Any | None = None,
    trace: TraceCollector | None = None,
    claim_id: str | None = None,
) -> PipelineContext:
    return asyncio.run(
        run_pipeline_async(
            submission,
            policy_terms,
            policy_version_id,
            policy_svc,
            llm_provider,
            trace,
            claim_id=claim_id,
        )
    )
