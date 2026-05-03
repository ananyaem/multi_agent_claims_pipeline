"""Streamlit UI — talks to the FastAPI service only (no direct DB imports)."""

from __future__ import annotations

import base64
import html as html_module
import json
import os
import uuid
from collections.abc import Callable
from typing import Any

import httpx
import pandas as pd
import streamlit as st
import streamlit.components.v1 as st_components

# --- HTTP / env (was ui.api) ---


# Server-side calls always use this (in Docker, http://api:8000 from the UI container).
INTERNAL_API = os.environ.get("CLAIMS_API_URL", "http://127.0.0.1:8000").rstrip("/")
# Links opened in the user's browser (empty env → same as INTERNAL_API).
_pub = (os.environ.get("PUBLIC_CLAIMS_API_URL") or "").strip()
PUBLIC_DEFAULT = (_pub if _pub else INTERNAL_API).rstrip("/")


def browser_api_base() -> str:
    """Host/port the member's browser can reach (CSV links, etc.)."""
    return st.session_state.get("api_base", PUBLIC_DEFAULT).rstrip("/")


def http_client(timeout: float = 120.0) -> httpx.Client:
    return httpx.Client(base_url=INTERNAL_API, timeout=timeout)


def http_get_json(
    path: str,
    *,
    timeout: float = 120.0,
    params: dict[str, Any] | None = None,
) -> Any:
    with http_client(timeout=timeout) as c:
        r = c.get(path, params=params)
    r.raise_for_status()
    return r.json()


def http_post_json(
    path: str,
    *,
    timeout: float = 120.0,
    json_body: Any | None = None,
    data: Any | None = None,
    files: Any | None = None,
) -> Any:
    with http_client(timeout=timeout) as c:
        r = c.post(path, json=json_body, data=data, files=files)
    r.raise_for_status()
    return r.json()

# --- Theme (was ui.theme) ---

# Streamlit UI theme (Plum-inspired). Google Fonts + Chromatica (sidebar) via CDNFonts stylesheet.
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Fraunces:wght@500;600;700"
    "&family=Plus+Jakarta+Sans:wght@400;600"
    "&family=Syne:wght@700;800"
    "&display=swap"
)
CHROMATICA_CSS_URL = "https://fonts.cdnfonts.com/css/chromatica"
PLUM = {
    "brand": "#ff4052",
    "sidebar_bg": "#3a0e2b",
    "ink": "#1d1d1f",
    "link": "#5f3a8a",
    "link_v": "#4a2d6b",
    "link_h": "#7b4db3",
    "api_url_field_bg": "#1d0716",
    "api_url_field_fg": "#fff1e5",
}


def plum_ui_css() -> str:
    """Single stylesheet: font imports + Plum sidebar / main content rules."""
    p = PLUM
    sb = '[data-testid="stSidebar"]'
    sc = '[data-testid="stSidebarContent"]'
    sec = 'section[data-testid="stSidebar"]'
    roots_ff = f"{sec}, {sb}, {sc}"
    roots_bg = f"{sec}, {sc}"
    return f"""<style>
@import url('{GOOGLE_FONTS_URL}');
@import url('{CHROMATICA_CSS_URL}');

html, body, .stApp {{
    font-family: "Plus Jakarta Sans", sans-serif;
}}

/* Chromatica on sidebar + descendants — !important beats Streamlit Emotion (.st-emotion-cache-*) */
{roots_ff} {{
    font-family: "Chromatica", "Plus Jakarta Sans", sans-serif !important;
}}

{sb} *:not(.sidebar-brand),
{sc} *:not(.sidebar-brand) {{
    font-family: "Chromatica", "Plus Jakarta Sans", sans-serif !important;
}}

{roots_bg} {{
    background-color: {p["sidebar_bg"]} !important;
}}

{sb} .block-container {{
    color: #ffffff !important;
}}

{sb} p:not(.sidebar-brand),
{sb} span,
{sb} label,
{sb} [data-baseweb="radio"] label,
{sb} [role="radiogroup"] label {{
    color: #ffffff !important;
}}

{sb} h1,
{sb} h2,
{sb} h3,
{sb} h4,
{sb} h5,
{sb} h6 {{
    color: #ffffff !important;
}}

{sb} input,
{sb} textarea {{
    background-color: rgba(255, 255, 255, 0.18) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.45) !important;
    caret-color: #ffffff;
}}

{sb} input::placeholder {{
    color: rgba(255, 255, 255, 0.75);
}}

/* API URL text input (key=api_base → .st-key-api_base): dark field, cream text */
{sb} .st-key-api_base input,
{sb} .st-key-api_base textarea {{
    background-color: {p["api_url_field_bg"]} !important;
    color: {p["api_url_field_fg"]} !important;
    border-color: rgba(255, 241, 229, 0.38) !important;
    caret-color: {p["api_url_field_fg"]} !important;
}}
{sb} .st-key-api_base input::placeholder {{
    color: rgba(255, 241, 229, 0.52) !important;
}}
{sb} .st-key-api_base [data-baseweb="base-input"],
{sb} .st-key-api_base [data-baseweb="input"] {{
    background-color: {p["api_url_field_bg"]} !important;
    color: {p["api_url_field_fg"]} !important;
}}

{sb} svg {{
    fill: #ffffff !important;
}}

{sb} p.sidebar-brand {{
    font-family: "Syne", sans-serif !important;
    font-weight: 800 !important;
    font-size: clamp(1.5rem, 3vw, 2rem);
    line-height: 1.0;
    color: {p["brand"]} !important;
    margin: 0 0 1rem 0 !important;
    padding: 0 !important;
    text-align: left;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: "Fraunces", Georgia, serif !important;
    color: {p["ink"]} !important;
}}

.stApp a:link {{ color: {p["link"]}; }}
.stApp a:visited {{ color: {p["link_v"]}; }}
.stApp a:hover {{ color: {p["link_h"]}; }}

div[data-testid="stButton"] button {{
    border-radius: 8px;
    font-weight: 600;
    border: none;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}}

/* Hide sidebar expand/collapse control (Material keyboard_double_arrow_* icon flicker) */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {{
    display: none !important;
}}
</style>"""


def inject_plum_styles() -> None:
    st.markdown(plum_ui_css(), unsafe_allow_html=True)

# --- Components (was ui.components; st_components = streamlit.components.v1) ---

import streamlit.components.v1 as st_components



def clipboard_copy_button(text: str, label: str = "Copy") -> None:
    """Client-side copy only (no Streamlit rerun). Payload passed as base64 to avoid HTML/quote issues."""
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    bid = uuid.uuid4().hex[:12]
    lab = html_module.escape(label)
    st_components.html(
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
    st_components.html(
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
    st_components.html(
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

# --- Claim status (was ui.claim_status) ---



SUBMIT_POLL_KEY = "submit_pending_claim_id"
SUBMIT_RESULT_KEY = "submit_claim_result"
SCROLL_SUBMIT_STATUS_KEY = "submit_scroll_to_status_footer"
SUBMIT_STATUS_ANCHOR_ID = "submit-claim-status-anchor"
POLL_INTERVAL_SEC = 5
LAST_SUBMITTED_CLAIM_KEY = "last_submitted_claim_id"


def claim_banner_payload(claim_id: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "status": data.get("status"),
        "decision": data.get("decision"),
        "approved_amount": data.get("approved_amount"),
        "member_message": data.get("member_message"),
    }


def claim_status_box(title: str, payload: dict[str, Any], *, accent: str | None = None) -> None:
    p = PLUM
    bar = accent or p["brand"]
    cid = html_module.escape(str(payload.get("claim_id") or "—"))
    status = html_module.escape(str(payload.get("status") or "—"))
    decision = payload.get("decision")
    decision_s = html_module.escape(str(decision) if decision is not None else "—")
    amt = html_module.escape(fmt_money(payload.get("approved_amount")))
    msg_raw = (payload.get("member_message") or "").strip() or "—"
    msg = html_module.escape(msg_raw).replace("\n", "<br/>")
    title_esc = html_module.escape(title)
    lab = "font-size: 0.95rem; font-weight: 600; color: rgba(29,29,31,0.52);"
    val = f'font-size: 1.05rem; color: {p["ink"]}; word-break: break-word;'
    row = (
        "display: grid; grid-template-columns: minmax(132px, 30%) 1fr; "
        "gap: 0.35rem 1rem; align-items: start; padding: 0.5rem 0; "
        "border-bottom: 1px solid rgba(29,29,31,0.07);"
    )
    st.markdown(
        f'<div style="border-radius: 16px; margin: 0 0 0.85rem 0; overflow: hidden; '
        f'box-shadow: 0 4px 14px rgba(29,29,31,0.1); border: 1px solid rgba(29,29,31,0.1); '
        f'background: linear-gradient(180deg, #ffffff 0%, #faf9fb 100%);">'
        f'<div style="display: flex; min-height: 100%;">'
        f'<div style="width: 6px; flex-shrink: 0; background: {bar};"></div>'
        f'<div style="padding: 1.15rem 1.35rem 1.25rem 1.35rem; flex: 1;">'
        f'<div style="font-size: 1.15rem; font-weight: 700; color: {p["ink"]}; letter-spacing: -0.02em;">'
        f"{title_esc}</div>"
        f'<div style="margin-top: 0.65rem;">'
        f'<div style="{row}"><span style="{lab}">Claim ID</span>'
        f'<span style="{val}"><code style="font-size:0.95em;">{cid}</code></span></div>'
        f'<div style="{row}"><span style="{lab}">Status</span><span style="{val}">{status}</span></div>'
        f'<div style="{row}"><span style="{lab}">Decision</span><span style="{val}">{decision_s}</span></div>'
        f'<div style="{row} border-bottom: none;"><span style="{lab}">Approved amount</span>'
        f'<span style="{val}">{amt}</span></div>'
        f"</div>"
        f'<div style="margin-top: 0.85rem; padding-top: 0.35rem;">'
        f'<div style="{lab} margin-bottom: 0.35rem;">Message</div>'
        f'<p style="margin: 0; font-size: 1.08rem; color: {p["ink"]}; line-height: 1.55;">{msg}</p>'
        f"</div>"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )
    cid_plain = payload.get("claim_id")
    if cid_plain:
        clipboard_copy_button(str(cid_plain), "Copy claim ID")


def render_submit_status_footer() -> None:
    pending = bool(st.session_state.get(SUBMIT_POLL_KEY))
    done = st.session_state.get(SUBMIT_RESULT_KEY)
    scroll = st.session_state.get(SCROLL_SUBMIT_STATUS_KEY)
    if not pending and not done and not scroll:
        return

    st.divider()
    st.markdown("### Claim status")
    st.markdown(
        '<p style="font-size: 1.05rem; color: rgba(29,29,31,0.72); margin: 0 0 0.25rem 0;">'
        "Live updates after you queue a claim — shown below the submit button.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div id="{SUBMIT_STATUS_ANCHOR_ID}" style="scroll-margin-top: 0.75rem;"></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.pop(SCROLL_SUBMIT_STATUS_KEY, False):
        scroll_to_anchor(SUBMIT_STATUS_ANCHOR_ID)

    done = st.session_state.get(SUBMIT_RESULT_KEY)
    if done:
        claim_status_box("Result", done, accent=PLUM["link"])
        if st.button("Dismiss", key="dismiss_completed_claim_banner"):
            st.session_state.pop(SUBMIT_RESULT_KEY, None)
            st.rerun()

    if st.session_state.get(SUBMIT_POLL_KEY):
        submit_claim_poll_fragment()


@st.fragment(run_every=POLL_INTERVAL_SEC)
def submit_claim_poll_fragment() -> None:
    cid = st.session_state.get(SUBMIT_POLL_KEY)
    if not cid:
        return
    try:
        data = http_get_json(f"/claims/{cid}", timeout=15.0)
    except Exception as e:
        st.warning(f"Could not load claim status (will retry): {e}")
        return

    payload = claim_banner_payload(cid, data)
    status = payload.get("status") or ""
    poll_refresh_countdown(interval_sec=POLL_INTERVAL_SEC)
    claim_status_box("Processing", payload)
    if st.button("Stop tracking", key="stop_claim_poll_banner"):
        st.session_state.pop(SUBMIT_POLL_KEY, None)
        st.rerun()
    if status in ("DONE", "HALTED"):
        st.session_state[SUBMIT_RESULT_KEY] = payload
        st.session_state.pop(SUBMIT_POLL_KEY, None)
        st.rerun()


def render_claim_detail_body(data: dict[str, Any]) -> None:
    cid = data.get("claim_id")
    if cid:
        h1, h2 = st.columns([5, 1])
        with h1:
            st.code(str(cid), language=None)
        with h2:
            clipboard_copy_button(str(cid), "Copy ID")
    st.json(data)
    steps = data.get("trace_steps") or []
    if steps:
        st.write("**Trace**")
        st.dataframe(pd.DataFrame(steps), use_container_width=True)

# --- Screen: submit.py ---




def page_submit() -> None:
    st.subheader("Submit claim")

    st.caption(
        "Claim categories and document upload slots come from the **active policy** "
        "`document_requirements` for the category you select. Use **➕** to attach extra files "
        "(choose a type, or **OTHERS** if unknown — queued for manual review)."
    )

    doc_type_options: list[str] = ["OTHERS"]
    try:
        doc_type_options = (
            http_get_json("/meta/document-types", timeout=15.0).get("document_types")
            or doc_type_options
        )
    except Exception:
        pass
    if "OTHERS" not in doc_type_options:
        doc_type_options = sorted([*doc_type_options, "OTHERS"])
    else:
        doc_type_options = sorted(doc_type_options)
    others_ix = doc_type_options.index("OTHERS") if "OTHERS" in doc_type_options else 0

    try:
        categories = http_get_json("/meta/claim-categories", timeout=15.0).get("claim_categories") or []
    except Exception as e:
        st.error(f"Could not load claim categories: {e}")
        categories = []

    policy_ids: list[str] = []
    try:
        policy_ids = http_get_json("/meta/policy-ids", timeout=15.0).get("policy_ids") or []
    except Exception as e:
        st.warning(f"Could not load policy ids: {e}")

    st.markdown("##### Claim details")
    col_a, col_b = st.columns(2)
    with col_a:
        member_id = st.text_input("member_id", value="EMP001", key="submit_member_id")
        _pidx = 0
        if policy_ids and "PLUM_GHI_2024" in policy_ids:
            _pidx = policy_ids.index("PLUM_GHI_2024")
        policy_id = st.selectbox(
            "policy_id",
            options=policy_ids if policy_ids else ["(no policies in database — run API seed or add via Policy page)"],
            index=_pidx if policy_ids else 0,
            disabled=not policy_ids,
            key="submit_policy_id",
        )
        treatment_date = st.text_input("treatment_date (YYYY-MM-DD)", value="2024-11-01", key="submit_treatment_date")
    with col_b:
        claimed = st.number_input("claimed_amount", min_value=0.0, value=5000.0, key="submit_claimed")
        hospital = st.text_input("hospital_name", value="Network Hospital", key="submit_hospital")
        ytd = st.text_input("ytd_claims_amount (optional)", value="", key="submit_ytd")

    st.markdown("##### Documents")
    st.caption("Choose claim category, then attach files below (slots follow the active policy for that category).")

    category = st.selectbox(
        "claim_category",
        options=categories if categories else ["(fix active policy — no document_requirements)"],
        disabled=not categories,
        key="submit_claim_category",
    )

    cat_ok = bool(categories) and not str(category).startswith("(")
    extra_key = f"extra_doc_slots_{category}" if cat_ok else "extra_doc_slots_invalid"

    if cat_ok:
        prev_cat_key = "_submit_prev_category"
        if st.session_state.get(prev_cat_key) != category:
            if str(category).upper() == "OTHERS":
                st.session_state[extra_key] = max(st.session_state.get(extra_key, 0), 1)
            st.session_state[prev_cat_key] = category

    reqs: dict = {"required": [], "optional": []}
    if cat_ok:
        try:
            reqs = http_get_json(f"/meta/document-requirements/{category}", timeout=15.0)
        except Exception as e:
            st.warning(f"Could not load document requirements: {e}")

    st.caption(
        f"Policy slots for **{category}** — Required: **{', '.join(reqs.get('required') or []) or '—'}** · "
        f"Optional: **{', '.join(reqs.get('optional') or []) or '—'}**"
    )
    if cat_ok and str(category).upper() == "OTHERS":
        st.info(
            "**OTHERS** has no fixed policy slots — we open at least one extra row automatically; "
            "use **OTHERS** as the type if unsure (manual review). Add more rows with **➕** below."
        )

    filed: dict[str, Any] = {}
    for dt in reqs.get("required") or []:
        filed[dt] = st.file_uploader(
            f"{dt} (required)",
            accept_multiple_files=True,
            key=f"req_{category}_{dt}",
        )
    for dt in reqs.get("optional") or []:
        filed[dt] = st.file_uploader(
            f"{dt} (optional)",
            accept_multiple_files=True,
            key=f"opt_{category}_{dt}",
        )

    st.caption("Add optional extra attachments (any document type) — placed after the policy slots above.")
    ex1, ex2, ex3 = st.columns([1, 2, 8])
    with ex1:
        if st.button(
            "➕",
            help="Add another document row (in addition to required/optional slots above).",
            disabled=not cat_ok,
            key="btn_add_extra_doc",
        ):
            st.session_state[extra_key] = st.session_state.get(extra_key, 0) + 1
            st.rerun()
    with ex2:
        if cat_ok and st.session_state.get(extra_key, 0) > 0:
            if st.button("Clear extra rows", key="btn_clear_extra_docs"):
                st.session_state[extra_key] = 0
                st.rerun()
    with ex3:
        if cat_ok and st.session_state.get(extra_key, 0):
            st.caption(f"Extra document rows: {st.session_state[extra_key]}")

    extra_n = st.session_state.get(extra_key, 0) if cat_ok else 0
    if extra_n > 0:
        st.divider()
        st.markdown("**Additional documents**")
        for i in range(extra_n):
            c1, c2 = st.columns([2, 3])
            with c1:
                st.selectbox(
                    f"Extra {i + 1} — document type",
                    options=doc_type_options,
                    index=others_ix,
                    key=f"extra_dtype_{category}_{i}",
                )
            with c2:
                st.file_uploader(f"Extra {i + 1} — file", key=f"extra_file_{category}_{i}")

    submitted = st.button("Submit", type="primary", key="btn_queue_claim")

    if submitted:
        if not policy_ids:
            st.error(
                "No policies in the database. Start the API (seed runs on startup) or save policy from the Policy page."
            )
            return
        if not categories or category.startswith("("):
            st.error("Select a valid claim category.")
            return
        data: dict = {
            "member_id": member_id,
            "policy_id": policy_id,
            "claim_category": category,
            "treatment_date": treatment_date,
            "claimed_amount": str(claimed),
            "hospital_name": hospital or "",
        }
        if ytd.strip():
            data["ytd_claims_amount"] = ytd.strip()

        files: list[tuple[str, tuple[str, bytes, str]]] = []
        for dt, fu in filed.items():
            if not fu:
                continue
            parts = fu if isinstance(fu, list) else [fu]
            for f in parts:
                ct = getattr(f, "type", None) or "application/octet-stream"
                files.append((f"docfile_{dt}", (f.name, f.getvalue(), ct)))

        ex_n = st.session_state.get(extra_key, 0) if not str(category).startswith("(") else 0
        for i in range(ex_n):
            edt = st.session_state.get(f"extra_dtype_{category}_{i}", "OTHERS")
            efu = st.session_state.get(f"extra_file_{category}_{i}")
            if not efu:
                continue
            ct = getattr(efu, "type", None) or "application/octet-stream"
            files.append((f"docfile_{edt}", (efu.name, efu.getvalue(), ct)))

        try:
            with http_client() as c:
                r = c.post("/claims/submit", data=data, files=files)
            r.raise_for_status()
            body = r.json()
            cid = body.get("claim_id")
            if cid:
                st.session_state[SUBMIT_POLL_KEY] = cid
                st.session_state[LAST_SUBMITTED_CLAIM_KEY] = cid
                st.session_state.pop(SUBMIT_RESULT_KEY, None)
            st.session_state[SCROLL_SUBMIT_STATUS_KEY] = True
            st.success(
                f"Claim **{cid}** submitted."
                if cid
                else "Claim submitted — tracking status below when `claim_id` is returned."
            )
            st.rerun()
        except Exception as e:
            st.error(str(e))

    render_submit_status_footer()

# --- Screen: claims.py ---




def page_claims() -> None:
    st.subheader("Claims")
    st.caption(
        "Click a row in the table to select a claim (round marker = single choice). "
        "Detail loads below immediately."
    )
    try:
        rows = http_get_json("/claims", params={"limit": 100})
        if not rows:
            st.info("No claims yet.")
            return
        df = pd.DataFrame(rows)
        claim_order = claim_ids_from_rows(rows)
        if not claim_order:
            st.warning("No claim IDs in the response.")
            return

        prefer = st.session_state.get(LAST_SUBMITTED_CLAIM_KEY)
        default_ix = claim_order.index(prefer) if prefer in claim_order else 0
        default_ix = min(default_ix, len(claim_order) - 1)

        # single-row-required → circular row markers (radio-like), not square checkboxes.
        sel_default: dict[str, Any] = {"selection": {"rows": [default_ix]}}
        state = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row-required",
            selection_default=sel_default,
            key="claims_df",
        )
        ix = dataframe_selected_row_index(
            state, fallback_ix=default_ix, row_count=len(claim_order)
        )
        picked_id = claim_order[ix]

        try:
            detail = http_get_json(f"/claims/{picked_id}")
            st.divider()
            render_claim_detail_body(detail)
        except Exception as e:
            st.error(str(e))
    except Exception as e:
        st.error(str(e))

# --- Screen: detail.py ---



def page_detail() -> None:
    st.subheader("Claim detail")
    cid = st.text_input("claim_id", key="detail_claim_id_input")
    if st.button("Load", key="detail_load_btn") and cid.strip():
        try:
            render_claim_detail_body(http_get_json(f"/claims/{cid.strip()}"))
        except Exception as e:
            st.error(str(e))

# --- Screen: analytics.py ---



def page_analytics() -> None:
    st.subheader("Decision analytics")
    try:
        rows = http_get_json("/analytics/decisions", params={"limit": 500})
        if not rows:
            st.info("No decision events yet.")
            return
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        csv_url = f"{browser_api_base()}/analytics/decisions.csv"
        st.markdown(f"[Download CSV]({csv_url})")
    except Exception as e:
        st.error(str(e))

# --- Screen: eval_run.py ---



def page_eval() -> None:
    st.subheader("Fixture eval (test_cases.json)")
    st.caption(
        "**Eval (fixtures)** runs offline against bundled cases in `assignment/test_cases.json`: "
        "each case seeds eval DB state, runs the pipeline with **no LLM**, and returns halted / decision / "
        "approved amount / confidence. Use this for **developer or QA** checks — not for live member claims."
    )
    if st.button("Run eval via API"):
        try:
            st.json(http_post_json("/eval/run", timeout=300.0))
        except Exception as e:
            st.error(str(e))

# --- Screen: policy.py ---




def format_policy_api_error(exc: Exception) -> None:
    """Show FastAPI / httpx errors; surfaces POST /admin/policy 422 validation list."""
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        try:
            payload = exc.response.json()
        except Exception:
            st.error(str(exc))
            return
        detail = payload.get("detail")
        if isinstance(detail, dict) and isinstance(detail.get("errors"), list):
            st.error("Policy validation failed:")
            for msg in detail["errors"]:
                st.markdown(f"- {msg}")
            return
        if isinstance(detail, list):
            st.error("Validation failed:")
            for msg in detail:
                st.markdown(f"- {msg}")
            return
        if detail is not None:
            st.error(str(detail))
            return
    st.error(str(exc))


def page_policy() -> None:
    st.subheader("Policy (active + versions)")
    st.caption(
        "**Formatted preview** opens by default (read-only tree). Switch to **Edit JSON** to change **terms**. "
        "Saving sends JSON to the API: the server runs **`validate_policy_terms`** "
        "(policy_id, coverage, opd_categories, document_requirements, members, etc.) — invalid payloads return **422** with a list of errors."
    )
    try:
        active = http_get_json("/policy/active")
    except Exception as e:
        st.error(str(e))
        return

    terms = active.get("terms") or {}
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Active policy_version_id", active.get("policy_version_id"))
    with m2:
        st.caption("Each save creates a new immutable version (or reactivates an identical hash).")

    tab_preview, tab_edit = st.tabs(["Formatted preview", "Edit JSON"])
    with tab_preview:
        raw = st.session_state.get("policy_editor", json.dumps(terms, indent=2))
        try:
            preview_obj = json.loads(raw)
            st.json(preview_obj, expanded=2)
        except json.JSONDecodeError:
            st.info("Switch to **Edit JSON** and fix syntax to see a formatted tree here.")

    with tab_edit:
        st.markdown(
            "<style>"
            "textarea[aria-label*='Policy terms'] {"
            "font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;"
            "font-size: 13px !important; line-height: 1.5 !important;"
            "}"
            "</style>",
            unsafe_allow_html=True,
        )
        edited = st.text_area(
            "Policy terms (JSON)",
            value=json.dumps(terms, indent=2),
            height=460,
            key="policy_editor",
            help="Monospace-friendly editor. Must be valid JSON and pass server validation.",
        )
        try:
            json.loads(edited)
            st.success("JSON syntax OK (local).")
        except json.JSONDecodeError as e:
            st.warning(f"JSON syntax: {e}")

    if st.button("Validate & save as active version", key="policy_save_btn"):
        edited_save = st.session_state.get("policy_editor", json.dumps(terms, indent=2))
        try:
            parsed = json.loads(edited_save)
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")
            return
        try:
            st.success(
                json.dumps(
                    http_post_json("/admin/policy", timeout=60.0, json_body={"terms": parsed}),
                    indent=2,
                )
            )
            st.rerun()
        except Exception as e:
            format_policy_api_error(e)

    with st.expander("All versions"):
        try:
            st.dataframe(pd.DataFrame(http_get_json("/policy/versions")), use_container_width=True)
        except Exception as e:
            st.error(str(e))

# --- Screen: health.py ---



def page_health() -> None:
    st.subheader("Health")
    try:
        st.json(http_get_json("/health", timeout=10.0))
    except Exception as e:
        st.error(str(e))

# --- Entry (was ui.app) ---



_NAV_ITEMS: list[tuple[str, Callable[[], None]]] = [
    ("Submit", page_submit),
    ("Claims", page_claims),
    ("Detail", page_detail),
    ("Analytics", page_analytics),
    ("Eval (fixtures)", page_eval),
    ("Policy", page_policy),
    ("Health", page_health),
]


def main() -> None:
    st.set_page_config(
        page_title="Claims pipeline",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_plum_styles()

    with st.sidebar:
        st.markdown(
            '<p class="sidebar-brand">Claims Pipeline</p>',
            unsafe_allow_html=True,
        )
        st.text_input(
            "API URL (browser links)",
            key="api_base",
            value=PUBLIC_DEFAULT,
            help="HTTP requests from this app use CLAIMS_API_URL. Adjust this if download links should point elsewhere.",
        )
        nav = st.radio(
            "Navigate",
            options=[label for label, _ in _NAV_ITEMS],
            label_visibility="collapsed",
        )

    dict(_NAV_ITEMS)[nav]()


if __name__ == "__main__":
    main()
