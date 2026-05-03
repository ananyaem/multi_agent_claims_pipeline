"""Submit claim page."""

from __future__ import annotations

from typing import Any

import streamlit as st

from claims_pipeline.ui import api
from claims_pipeline.ui.claim_status import (
    LAST_SUBMITTED_CLAIM_KEY,
    SCROLL_SUBMIT_STATUS_KEY,
    SUBMIT_POLL_KEY,
    SUBMIT_RESULT_KEY,
    render_submit_status_footer,
)


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
            api.http_get_json("/meta/document-types", timeout=15.0).get("document_types")
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
        categories = api.http_get_json("/meta/claim-categories", timeout=15.0).get("claim_categories") or []
    except Exception as e:
        st.error(f"Could not load claim categories: {e}")
        categories = []

    policy_ids: list[str] = []
    try:
        policy_ids = api.http_get_json("/meta/policy-ids", timeout=15.0).get("policy_ids") or []
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
            reqs = api.http_get_json(f"/meta/document-requirements/{category}", timeout=15.0)
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
            with api.http_client() as c:
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
