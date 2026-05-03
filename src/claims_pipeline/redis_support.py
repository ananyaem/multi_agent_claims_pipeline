from __future__ import annotations

import logging
import threading
import time
from typing import Callable

import redis

from claims_pipeline.config import get_settings

logger = logging.getLogger(__name__)


def redis_client() -> redis.Redis:
    return redis.from_url(get_settings().redis_url, decode_responses=False)


def start_worker_heartbeat(
    r: redis.Redis,
    name: str,
    *,
    interval_sec: float = 15.0,
    ttl_sec: int = 45,
) -> None:
    """Background thread: SET worker:heartbeat:{name} so /health can tell if the process is up."""

    key = f"worker:heartbeat:{name}"

    def _loop() -> None:
        while True:
            try:
                r.set(key, str(time.time()), ex=ttl_sec)
            except Exception as e:
                logger.warning("worker heartbeat %s: %s", name, e)
            time.sleep(interval_sec)

    threading.Thread(target=_loop, daemon=True, name=f"heartbeat-{name}").start()


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
