"""Decision analytics table + CSV link."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from claims_pipeline.ui import api


def page_analytics() -> None:
    st.subheader("Decision analytics")
    try:
        rows = api.http_get_json("/analytics/decisions", params={"limit": 500})
        if not rows:
            st.info("No decision events yet.")
            return
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        csv_url = f"{api.browser_api_base()}/analytics/decisions.csv"
        st.markdown(f"[Download CSV]({csv_url})")
    except Exception as e:
        st.error(str(e))
