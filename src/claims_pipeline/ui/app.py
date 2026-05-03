"""Streamlit entrypoint: sidebar, navigation, page dispatch."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from claims_pipeline.ui import theme
from claims_pipeline.ui.api import PUBLIC_DEFAULT
from claims_pipeline.ui.screens import analytics, claims, detail, eval_run, health, policy, submit

_NAV_ITEMS: list[tuple[str, Callable[[], None]]] = [
    ("Submit", submit.page_submit),
    ("Claims", claims.page_claims),
    ("Detail", detail.page_detail),
    ("Analytics", analytics.page_analytics),
    ("Eval (fixtures)", eval_run.page_eval),
    ("Policy", policy.page_policy),
    ("Health", health.page_health),
]


def main() -> None:
    st.set_page_config(
        page_title="Claims pipeline",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    theme.inject_plum_styles()

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
