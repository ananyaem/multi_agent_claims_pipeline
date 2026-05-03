"""Claims list + dataframe row selection + detail."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from claims_pipeline.ui import api
from claims_pipeline.ui import components
from claims_pipeline.ui.claim_status import LAST_SUBMITTED_CLAIM_KEY, render_claim_detail_body


def page_claims() -> None:
    st.subheader("Claims")
    st.caption(
        "Click a row in the table to select a claim (round marker = single choice). "
        "Detail loads below immediately."
    )
    try:
        rows = api.http_get_json("/claims", params={"limit": 100})
        if not rows:
            st.info("No claims yet.")
            return
        df = pd.DataFrame(rows)
        claim_order = components.claim_ids_from_rows(rows)
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
        ix = components.dataframe_selected_row_index(
            state, fallback_ix=default_ix, row_count=len(claim_order)
        )
        picked_id = claim_order[ix]

        try:
            detail = api.http_get_json(f"/claims/{picked_id}")
            st.divider()
            render_claim_detail_body(detail)
        except Exception as e:
            st.error(str(e))
    except Exception as e:
        st.error(str(e))
