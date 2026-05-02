from __future__ import annotations

import logging
from typing import Sequence

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
    step_confidences: Sequence[float],
    degraded_agents: Sequence[str],
    penalty: float = DEFAULT_DEGRADED_PENALTY,
    eps: float = EPS,
) -> float:
    combined = list(step_confidences)
    for _ in degraded_agents:
        combined.append(penalty)
    return harmonic_mean(combined, eps=eps)
