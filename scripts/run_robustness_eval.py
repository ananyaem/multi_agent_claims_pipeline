#!/usr/bin/env python3
"""Optional: run variant images through Gemini extraction when fixtures/docs populated."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    fix = ROOT / "fixtures" / "docs"
    out = ROOT / "docs" / "ROBUSTNESS_REPORT.md"
    lines = [
        f"# ROBUSTNESS_REPORT\n\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n",
    ]
    if not fix.exists() or not os.environ.get("GEMINI_API_KEY"):
        lines.append(
            "**Status:** skipped — generate `fixtures/docs` (see `gen_sample_docs.py`) "
            "and set `GEMINI_API_KEY` to run 48 variant extractions.\n"
        )
    else:
        lines.append("**Status:** placeholder — wire image paths → `GeminiProvider` batch.\n")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
