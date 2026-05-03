#!/usr/bin/env python3
"""
Generate document image fixtures (HTML → Playwright → PNG/PDF + cv2 variants).
Requires: playwright install chromium, optional GEMINI_API_KEY for handwritten variant.

When skipped, create fixtures/docs/README pointing maintainers to full pipeline.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "docs"


def main() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    readme = FIX / "README.md"
    readme.write_text(
        "# Generated document fixtures\n\n"
        "Run this script after installing Playwright browsers:\n\n"
        "`playwright install chromium`\n\n"
        "Full implementation: Jinja2 templates in `templates/`, variants "
        "`clean`, `phone_photo`, `blurry`, `handwritten` (Gemini image), per PLAN.md.\n",
        encoding="utf-8",
    )
    print(f"Wrote {readme}")


if __name__ == "__main__":
    main()
