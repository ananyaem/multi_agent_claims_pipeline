"""Single claim detail by ID."""

from __future__ import annotations

import streamlit as st

from claims_pipeline.ui import api
from claims_pipeline.ui.claim_status import render_claim_detail_body


def page_detail() -> None:
    st.subheader("Claim detail")
    cid = st.text_input("claim_id", key="detail_claim_id_input")
    if st.button("Load", key="detail_load_btn") and cid.strip():
        try:
            render_claim_detail_body(api.http_get_json(f"/claims/{cid.strip()}"))
        except Exception as e:
            st.error(str(e))
