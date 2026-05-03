"""Reusable Streamlit UI bits: copy button, money format, dataframe selection helpers."""

from __future__ import annotations

import base64
import html as html_module
import uuid
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from claims_pipeline.ui.theme import PLUM


def clipboard_copy_button(text: str, label: str = "Copy") -> None:
    """Client-side copy only (no Streamlit rerun). Payload passed as base64 to avoid HTML/quote issues."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    bid = uuid.uuid4().hex[:12]
    lab = html_module.escape(label)
    components.html(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body style="margin:0;">
<button type="button" id="cb_{bid}"
  style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.82rem;font-weight:600;
  padding:0.35rem 0.65rem;border-radius:8px;border:1px solid rgba(95,58,138,0.35);
  background:#fff;color:{html_module.escape(PLUM["link"])};cursor:pointer;">
  {lab}
</button>
<script>
(function () {{
  var btn = document.getElementById("cb_{bid}");
  if (!btn) return;
  btn.addEventListener("click", function () {{
    var raw = atob("{b64}");
    var bytes = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    var t = new TextDecoder("utf-8").decode(bytes);
    navigator.clipboard.writeText(t);
  }});
}})();
</script>
</body></html>""",
        height=38,
    )


def fmt_money(v: Any) -> str:
    if v is None:
        return "—"
    try:
        return f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return str(v)


def claim_ids_from_rows(rows: list[Any]) -> list[str]:
    return [str(r["claim_id"]) for r in rows if isinstance(r, dict) and r.get("claim_id")]


def dataframe_selected_row_index(state: Any, *, fallback_ix: int, row_count: int) -> int:
    if row_count <= 0:
        return 0
    fb = min(max(fallback_ix, 0), row_count - 1)
    sel_rows: list[int] = []
    if isinstance(state, dict):
        raw = (state.get("selection") or {}).get("rows")
        if isinstance(raw, list):
            sel_rows = [int(x) for x in raw if isinstance(x, int)]
    else:
        sel = getattr(state, "selection", None)
        if sel is not None:
            raw = getattr(sel, "rows", None)
            if isinstance(raw, list):
                sel_rows = [int(x) for x in raw if isinstance(x, int)]
    if not sel_rows:
        return fb
    ix = sel_rows[0]
    if not isinstance(ix, int):
        return fb
    return min(max(ix, 0), row_count - 1)


def poll_refresh_countdown(*, interval_sec: int) -> None:
    """Browser-side countdown; ticks every second while the Streamlit fragment polls every `interval_sec`."""
    iv = int(interval_sec)
    components.html(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body style="margin:0;">
<div style="font-family: 'Plus Jakarta Sans', Helvetica, sans-serif; padding: 0 0 2px 0;
     font-size: 0.88rem; font-weight: 400; letter-spacing: 0.01em;
     color: rgba(29,29,31,0.48); line-height: 1.35;">
  Refresh in
  <span id="poll-cd" style="display: inline-block; min-width: 1.15em; text-align: center;
        margin: 0 0.15em 0 0.28em; padding: 0 6px; border-radius: 999px;
        font-size: 0.82rem; font-weight: 600; font-variant-numeric: tabular-nums;
        color: rgba(29,29,31,0.62);
        background: rgba(95,58,138,0.07); border: 1px solid rgba(95,58,138,0.14);">{iv}</span>
  s
</div>
<script>
(function () {{
  var n = {iv};
  var reset = {iv};
  var el = document.getElementById('poll-cd');
  if (!el) return;
  setInterval(function () {{
    n -= 1;
    if (n < 1) n = reset;
    el.textContent = n;
  }}, 1000);
}})();
</script>
</body></html>""",
        height=30,
    )


def scroll_to_anchor(anchor_id: str) -> None:
    aid = html_module.escape(anchor_id)
    components.html(
        f"""<script>
const doc = window.parent.document;
const el = doc.getElementById("{aid}");
if (el) {{
  el.scrollIntoView({{behavior: "smooth", block: "start"}});
}}
</script>""",
        height=1,
        width=1,
    )
