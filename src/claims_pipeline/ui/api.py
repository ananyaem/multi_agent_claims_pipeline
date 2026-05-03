"""HTTP client + JSON helpers for the Streamlit UI (calls FastAPI only)."""

from __future__ import annotations

import os
from typing import Any

import httpx
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


def http_get_json(
    path: str,
    *,
    timeout: float = 120.0,
    params: dict[str, Any] | None = None,
) -> Any:
    with http_client(timeout=timeout) as c:
        r = c.get(path, params=params)
    r.raise_for_status()
    return r.json()


def http_post_json(
    path: str,
    *,
    timeout: float = 120.0,
    json_body: Any | None = None,
    data: Any | None = None,
    files: Any | None = None,
) -> Any:
    with http_client(timeout=timeout) as c:
        r = c.post(path, json=json_body, data=data, files=files)
    r.raise_for_status()
    return r.json()
