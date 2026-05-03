from __future__ import annotations

import time
from typing import Callable

import redis

from claims_pipeline.config import get_settings


def redis_client() -> redis.Redis:
    return redis.from_url(get_settings().redis_url, decode_responses=False)


class TokenBucket:
    """Simple rate limiter for LLM worker."""

    def __init__(self, rpm: int):
        self.interval = 60.0 / max(rpm, 1)
        self._last = 0.0

    def acquire(self) -> None:
        now = time.monotonic()
        wait = self._last + self.interval - now
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()
