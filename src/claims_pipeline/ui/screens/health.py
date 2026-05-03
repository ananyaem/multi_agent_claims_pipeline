"""Health check page."""

from __future__ import annotations

import streamlit as st

from claims_pipeline.ui import api


def page_health() -> None:
    st.subheader("Health")
    try:
        st.json(api.http_get_json("/health", timeout=10.0))
    except Exception as e:
        st.error(str(e))
