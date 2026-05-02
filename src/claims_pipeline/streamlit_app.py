"""Streamlit UI — talks to the FastAPI service only (no direct DB imports)."""

from __future__ import annotations

import json
import os

import httpx
import pandas as pd
import streamlit as st

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


def page_health():
    st.subheader("Health")
    try:
        with http_client(timeout=10.0) as c:
            r = c.get("/health")
        st.json(r.json())
    except Exception as e:
        st.error(str(e))


def page_submit():
    st.subheader("Submit claim")
    with st.form("submit"):
        member_id = st.text_input("member_id", value="EMP001")
        policy_id = st.text_input("policy_id", value="PLUM_GHI_2024")
        category = st.selectbox(
            "claim_category",
            ["CONSULTATION", "PHARMACY", "DENTAL", "SURGERY", "DIAGNOSTICS"],
        )
        claimed = st.number_input("claimed_amount", min_value=0.0, value=5000.0)
        treatment_date = st.text_input("treatment_date (YYYY-MM-DD)", value="2024-11-01")
        hospital = st.text_input("hospital_name", value="Network Hospital")
        docs_json = st.text_area(
            "documents (JSON array of DocumentInput)",
            value=json.dumps(
                [
                    {"file_id": "UI001", "file_name": "rx.jpg", "actual_type": "PRESCRIPTION"},
                    {"file_id": "UI002", "file_name": "bill.jpg", "actual_type": "HOSPITAL_BILL"},
                ],
                indent=2,
            ),
        )
        submitted = st.form_submit_button("Queue claim")
    if submitted:
        try:
            documents = json.loads(docs_json)
        except json.JSONDecodeError as e:
            st.error(f"Invalid documents JSON: {e}")
            return
        body = {
            "member_id": member_id,
            "policy_id": policy_id,
            "claim_category": category,
            "claimed_amount": claimed,
            "treatment_date": treatment_date,
            "hospital_name": hospital or None,
            "documents": documents,
        }
        try:
            with http_client() as c:
                r = c.post("/claims", json=body)
            r.raise_for_status()
            st.success(json.dumps(r.json(), indent=2))
        except Exception as e:
            st.error(str(e))


def page_claims():
    st.subheader("Claims")
    try:
        with http_client() as c:
            r = c.get("/claims", params={"limit": 100})
        r.raise_for_status()
        rows = r.json()
        if not rows:
            st.info("No claims yet.")
            return
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    except Exception as e:
        st.error(str(e))


def page_detail():
    st.subheader("Claim detail")
    cid = st.text_input("claim_id")
    if st.button("Load") and cid.strip():
        try:
            with http_client() as c:
                r = c.get(f"/claims/{cid.strip()}")
            r.raise_for_status()
            data = r.json()
            st.json(data)
            steps = data.get("trace_steps") or []
            if steps:
                st.write("**Trace**")
                st.dataframe(pd.DataFrame(steps), use_container_width=True)
        except Exception as e:
            st.error(str(e))


def page_analytics():
    st.subheader("Decision analytics")
    try:
        with http_client() as c:
            r = c.get("/analytics/decisions", params={"limit": 500})
        r.raise_for_status()
        rows = r.json()
        if not rows:
            st.info("No decision events yet.")
            return
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        csv_url = f"{browser_api_base()}/analytics/decisions.csv"
        st.markdown(f"[Download CSV]({csv_url})")
    except Exception as e:
        st.error(str(e))


def page_eval():
    st.subheader("Fixture eval (test_cases.json)")
    if st.button("Run eval via API"):
        try:
            with http_client(timeout=300.0) as c:
                r = c.post("/eval/run")
            r.raise_for_status()
            st.json(r.json())
        except Exception as e:
            st.error(str(e))


def page_policy():
    st.subheader("Active policy")
    try:
        with http_client() as c:
            r = c.get("/policy/active")
        r.raise_for_status()
        st.json(r.json())
    except Exception as e:
        st.error(str(e))


def main():
    st.set_page_config(page_title="Claims pipeline", layout="wide")
    st.title("Claims pipeline")

    with st.sidebar:
        st.text_input(
            "API URL (browser links)",
            key="api_base",
            value=PUBLIC_DEFAULT,
            help="HTTP requests from this app use CLAIMS_API_URL. Adjust this if download links should point elsewhere.",
        )
        nav = st.radio(
            "Navigate",
            ["Health", "Submit", "Claims", "Detail", "Analytics", "Eval", "Policy"],
            label_visibility="collapsed",
        )

    if nav == "Health":
        page_health()
    elif nav == "Submit":
        page_submit()
    elif nav == "Claims":
        page_claims()
    elif nav == "Detail":
        page_detail()
    elif nav == "Analytics":
        page_analytics()
    elif nav == "Eval":
        page_eval()
    else:
        page_policy()


if __name__ == "__main__":
    main()
