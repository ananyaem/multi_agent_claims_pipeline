#!/usr/bin/env python3
"""Optional: run variant images through Gemini extraction when fixtures/TC* populated."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    fix = ROOT / "fixtures"
    legacy_docs = fix / "docs"
    has_fixtures = (fix.is_dir() and any(
        p.is_dir() and p.name.startswith("TC") and any(p.iterdir())
        for p in fix.iterdir()
    )) or (legacy_docs.is_dir() and any(legacy_docs.iterdir()))
    out = ROOT / "docs" / "ROBUSTNESS_REPORT.md"
    lines = [
        f"# ROBUSTNESS_REPORT\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n",
    ]
    if not has_fixtures or not os.environ.get("GEMINI_API_KEY"):
        lines.append(
            "**Status:** skipped — generate `fixtures/TC*/` (see `gen_sample_docs.py`) "
            "and set `GEMINI_API_KEY` to run variant extractions.\n"
        )
    else:
        lines.append("**Status:** placeholder — wire image paths → `GeminiProvider` batch.\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
