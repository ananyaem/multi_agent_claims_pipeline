"""Image sharpness / blur signals for document readability (no UI input)."""

from __future__ import annotations

import io
import logging
from typing import Any

logger = logging.getLogger(__name__)


def laplacian_variance(image_bytes: bytes) -> float | None:
    """
    Variance of the Laplacian — low values strongly correlate with heavy blur.
    Returns None if the bytes are not a decodable image.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        return None

    try:
        im = Image.open(io.BytesIO(image_bytes))
        im = im.convert("L")
        a = np.asarray(im, dtype=np.float64)
        if a.size < 9:
            return None
        lap = (
            -4.0 * a[1:-1, 1:-1]
            + a[:-2, 1:-1]
            + a[2:, 1:-1]
            + a[1:-1, :-2]
            + a[1:-1, 2:]
        )
        return float(np.var(lap))
    except Exception:
        logger.debug("laplacian_variance failed", exc_info=True)
        return None


def assess_image_bytes(image_bytes: bytes | None) -> dict[str, Any]:
    """Attach numeric sharpness for audit trails."""
    if not image_bytes:
        return {"laplacian_variance": None, "image_readable_hint": "no_image_bytes"}
    v = laplacian_variance(image_bytes)
    out: dict[str, Any] = {"laplacian_variance": v}
    if v is None:
        out["image_readable_hint"] = "unknown"
    elif v < 35.0:
        out["image_readable_hint"] = "very_low_sharpness"
    elif v < 90.0:
        out["image_readable_hint"] = "low_sharpness"
    else:
        out["image_readable_hint"] = "adequate_sharpness"
    return out
