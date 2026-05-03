"""Resize/recompress images before vision LLM calls (token + latency)."""

from __future__ import annotations

import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Balanced for Gemini vision: readable text, smaller payload.
_MAX_LONG_SIDE = 1280
_JPEG_QUALITY = 82


def compress_for_llm_vision(image_bytes: bytes, mime_type: str | None) -> Tuple[bytes, str]:
    """Return JPEG bytes (compressed) and mime image/jpeg when possible."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return image_bytes, mime_type or "image/jpeg"

    try:
        im = Image.open(io.BytesIO(image_bytes))
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        elif im.mode == "L":
            im = im.convert("RGB")

        w, h = im.size
        long_side = max(w, h)
        if long_side > _MAX_LONG_SIDE:
            scale = _MAX_LONG_SIDE / float(long_side)
            nw = max(1, int(round(w * scale)))
            nh = max(1, int(round(h * scale)))
            im = im.resize((nw, nh), Image.Resampling.LANCZOS)

        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
        out = buf.getvalue()
        if len(out) >= len(image_bytes) and (mime_type or "").lower() in ("image/jpeg", "image/jpg"):
            return image_bytes, "image/jpeg"
        return out, "image/jpeg"
    except Exception:
        logger.debug("compress_for_llm_vision fallback to original", exc_info=True)
        return image_bytes, mime_type or "image/jpeg"
