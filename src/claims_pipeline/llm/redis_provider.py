from __future__ import annotations

import json
import uuid
from typing import Any

import redis

from claims_pipeline.config import get_settings
from claims_pipeline.llm.base import LLMProvider


class RedisLLMProvider(LLMProvider):
    """Queues extraction to llm_worker via Redis; blocks on response list."""

    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client
        self.settings = get_settings()

    def extract_document(
        self,
        claim_id: str,
        file_id: str,
        doc_type: str,
        image_bytes: bytes | None,
        mime_type: str | None,
        hint: str,
    ) -> tuple[dict[str, Any], float]:
        req_id = str(uuid.uuid4())
        payload = {
            "req_id": req_id,
            "claim_id": claim_id,
            "file_id": file_id,
            "doc_type": doc_type,
            "mime_type": mime_type,
            "hint": hint,
            "image_b64": None,
        }
        if image_bytes:
            import base64

            payload["image_b64"] = base64.standard_b64encode(image_bytes).decode("ascii")

        self.r.rpush(self.settings.llm_queue, json.dumps(payload))
        key = f"llm:result:{req_id}"
        raw = self.r.blpop(key, timeout=self.settings.llm_request_timeout_sec)
        if raw is None:
            raise TimeoutError("LLM worker response timeout")
        _, body = raw
        msg = json.loads(body.decode("utf-8"))
        if not msg.get("ok"):
            raise RuntimeError(msg.get("error", "LLM failure"))
        return msg.get("data") or {}, float(msg.get("confidence", 0.5))
