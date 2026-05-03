"""Submit-page claim status card, polling fragment, and shared claim detail body."""

from __future__ import annotations

import html as html_module
from typing import Any

import pandas as pd
import streamlit as st

from claims_pipeline.ui import api
from claims_pipeline.ui import components
from claims_pipeline.ui.theme import PLUM

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
    amt = html_module.escape(components.fmt_money(payload.get("approved_amount")))
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
        components.clipboard_copy_button(str(cid_plain), "Copy claim ID")


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
        components.scroll_to_anchor(SUBMIT_STATUS_ANCHOR_ID)

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
        data = api.http_get_json(f"/claims/{cid}", timeout=15.0)
    except Exception as e:
        st.warning(f"Could not load claim status (will retry): {e}")
        return

    payload = claim_banner_payload(cid, data)
    status = payload.get("status") or ""
    components.poll_refresh_countdown(interval_sec=POLL_INTERVAL_SEC)
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
            components.clipboard_copy_button(str(cid), "Copy ID")
    st.json(data)
    steps = data.get("trace_steps") or []
    if steps:
        st.write("**Trace**")
        st.dataframe(pd.DataFrame(steps), use_container_width=True)
