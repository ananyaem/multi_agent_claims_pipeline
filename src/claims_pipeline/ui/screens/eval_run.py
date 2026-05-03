"""Fixture eval trigger page."""

from __future__ import annotations

import streamlit as st

from claims_pipeline.ui import api


def page_eval() -> None:
    st.subheader("Fixture eval (test_cases.json)")
    st.caption(
        "**Eval (fixtures)** runs offline against bundled cases in `assignment/test_cases.json`: "
        "each case seeds eval DB state, runs the pipeline with **no LLM**, and returns halted / decision / "
        "approved amount / confidence. Use this for **developer or QA** checks — not for live member claims."
    )
    if st.button("Run eval via API"):
        try:
            st.json(api.http_post_json("/eval/run", timeout=300.0))
        except Exception as e:
            st.error(str(e))
