from __future__ import annotations

import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable

from sqlalchemy.orm import Session

from claims_pipeline.db import LLMCallORM, TraceStepORM


_current_claim_id: ContextVar[str | None] = ContextVar("claim_id", default=None)


def set_claim_trace_context(claim_id: str) -> None:
    _current_claim_id.set(claim_id)


@dataclass
class TraceCollector:
    claim_id: str
    seq: int = 0
    steps: list[dict[str, Any]] = field(default_factory=list)
    llm_entries: list[dict[str, Any]] = field(default_factory=list)

    def emit_step(
        self,
        stage: str,
        status: str,
        findings: list[str] | dict[str, Any],
        duration_ms: int | None = None,
        confidence: float | None = None,
        inputs_summary: dict[str, Any] | None = None,
        outputs_summary: dict[str, Any] | None = None,
    ) -> None:
        self.seq += 1
        self.steps.append(
            {
                "seq": self.seq,
                "stage": stage,
                "status": status,
                "findings": findings,
                "duration_ms": duration_ms,
                "confidence": confidence,
                "inputs_summary": inputs_summary or {},
                "outputs_summary": outputs_summary or {},
            }
        )

    def persist(self, db: Session | None) -> None:
        if db is None:
            return
        for s in self.steps:
            db.add(
                TraceStepORM(
                    claim_id=self.claim_id,
                    seq=s["seq"],
                    stage=s["stage"],
                    status=s["status"],
                    findings=s["findings"],
                    inputs_summary=s.get("inputs_summary"),
                    outputs_summary=s.get("outputs_summary"),
                    duration_ms=s.get("duration_ms"),
                    confidence=s.get("confidence"),
                )
            )
        for L in self.llm_entries:
            db.add(LLMCallORM(**L))
        db.commit()


def safe_run(
    stage: str,
    collector: TraceCollector | None,
    fn: Callable[[], None],
    ctx_degraded: list[str],
    on_except: str = "FraudAgent",
) -> None:
    t0 = time.perf_counter()
    try:
        fn()
        ms = int((time.perf_counter() - t0) * 1000)
        if collector:
            collector.emit_step(stage, "OK", [stage], duration_ms=ms, confidence=None)
    except Exception as e:
        ms = int((time.perf_counter() - t0) * 1000)
        ctx_degraded.append(on_except)
        if collector:
            collector.emit_step(stage, "FAILED", [str(e)], duration_ms=ms, confidence=0.5)

