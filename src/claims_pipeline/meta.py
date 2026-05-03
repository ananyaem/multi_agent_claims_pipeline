"""Metadata derived from fixtures (e.g. test_cases.json) for UI and validation."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from claims_pipeline.config import TEST_CASES_PATH


def _walk(o: Any, out: set[str]) -> None:
    if isinstance(o, dict):
        at = o.get("actual_type")
        if isinstance(at, str) and at.strip():
            out.add(at.strip())
        for v in o.values():
            _walk(v, out)
    elif isinstance(o, list):
        for x in o:
            _walk(x, out)


@lru_cache
def document_types_from_test_cases(path: str | None = None) -> tuple[str, ...]:
    """Sorted unique `actual_type` values referenced in test_cases.json."""
    p = Path(path) if path else TEST_CASES_PATH
    with open(p, encoding="utf-8") as f:
        bundle = json.load(f)
    found: set[str] = set()
    _walk(bundle.get("test_cases", []), found)
    return tuple(sorted(found))
