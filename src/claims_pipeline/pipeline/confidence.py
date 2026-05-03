from __future__ import annotations

import logging
from typing import Any, Sequence

logger = logging.getLogger(__name__)

EPS = 0.01
DEFAULT_DEGRADED_PENALTY = 0.5


def harmonic_mean(confidences: Sequence[float], eps: float = EPS) -> float:
    """F1-style aggregation: weak links dominate."""
    vals = list(confidences)
    if not vals:
        logger.warning("harmonic_mean: empty sequence -> 0")
        return 0.0
    inv_sum = sum(1.0 / max(c, eps) for c in vals)
    return len(vals) / inv_sum


def aggregate_claim_confidence(
    records: Sequence[tuple[str, float]],
    degraded_agents: Sequence[str],
    penalty: float = DEFAULT_DEGRADED_PENALTY,
    eps: float = EPS,
) -> tuple[float, dict[str, Any]]:
    combined = [c for _, c in records]
    for _ in degraded_agents:
        combined.append(penalty)
    overall = harmonic_mean(combined, eps=eps) if combined else 0.0
    breakdown: dict[str, Any] = {
        "overall": round(overall, 6),
        "formula": "harmonic_mean_with_degraded_penalty",
        "description": (
            "Overall confidence is the harmonic mean of named pipeline step scores in [0,1]; "
            "lower scores dominate (weakest link). Each degraded component adds one penalty score "
            f"({penalty}) into the same mean — it is not an arithmetic average of headline numbers."
        ),
        "steps": {name: round(c, 6) for name, c in records},
        "degraded_penalty_each": penalty,
        "degraded_components": list(degraded_agents),
    }
    return overall, breakdown
