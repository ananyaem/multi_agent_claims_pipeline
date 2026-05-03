"""Active policy editor + versions."""

from __future__ import annotations

import json

import httpx
import pandas as pd
import streamlit as st

from claims_pipeline.ui import api


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
        active = api.http_get_json("/policy/active")
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
                    api.http_post_json("/admin/policy", timeout=60.0, json_body={"terms": parsed}),
                    indent=2,
                )
            )
            st.rerun()
        except Exception as e:
            format_policy_api_error(e)

    with st.expander("All versions"):
        try:
            st.dataframe(pd.DataFrame(api.http_get_json("/policy/versions")), use_container_width=True)
        except Exception as e:
            st.error(str(e))
