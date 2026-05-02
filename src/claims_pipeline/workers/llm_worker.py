"""Consume llm:queue, call Gemini, push llm:result:{req_id}."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from claims_pipeline.config import get_settings
from claims_pipeline.llm.gemini import GeminiProvider
from claims_pipeline.queue import TokenBucket, redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    r = redis_client()
    gemini = GeminiProvider()
    bucket = TokenBucket(settings.llm_rate_limit_rpm)

    logger.info("LLM worker listening on %s", settings.llm_queue)
    while True:
        item = r.blpop(settings.llm_queue, timeout=0)
        if item is None:
            continue
        _, raw = item
        payload = json.loads(raw.decode("utf-8"))
        req_id = payload["req_id"]
        key = f"llm:result:{req_id}"
        bucket.acquire()
        try:
            import base64

            img = None
            if payload.get("image_b64"):
                img = base64.standard_b64decode(payload["image_b64"])
            data, conf = gemini.extract_document(
                payload["claim_id"],
                payload["file_id"],
                payload["doc_type"],
                img,
                payload.get("mime_type"),
                payload.get("hint") or "",
            )
            out = json.dumps({"ok": True, "data": data, "confidence": conf})
        except Exception as e:
            logger.exception(e)
            out = json.dumps({"ok": False, "error": str(e)})
        r.rpush(key, out)


if __name__ == "__main__":
    main()
