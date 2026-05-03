"""Plum theme: font URLs + CSS injected into Streamlit."""

from __future__ import annotations

import streamlit as st

# Streamlit UI theme (Plum-inspired). Google Fonts + Chromatica (sidebar) via CDNFonts stylesheet.
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2"
    "?family=Fraunces:wght@500;600;700"
    "&family=Plus+Jakarta+Sans:wght@400;600"
    "&family=Syne:wght@700;800"
    "&display=swap"
)
CHROMATICA_CSS_URL = "https://fonts.cdnfonts.com/css/chromatica"
PLUM = {
    "brand": "#ff4052",
    "sidebar_bg": "#3a0e2b",
    "ink": "#1d1d1f",
    "link": "#5f3a8a",
    "link_v": "#4a2d6b",
    "link_h": "#7b4db3",
    "api_url_field_bg": "#1d0716",
    "api_url_field_fg": "#fff1e5",
}


def plum_ui_css() -> str:
    """Single stylesheet: font imports + Plum sidebar / main content rules."""
    p = PLUM
    sb = '[data-testid="stSidebar"]'
    sc = '[data-testid="stSidebarContent"]'
    sec = 'section[data-testid="stSidebar"]'
    roots_ff = f"{sec}, {sb}, {sc}"
    roots_bg = f"{sec}, {sc}"
    return f"""<style>
@import url('{GOOGLE_FONTS_URL}');
@import url('{CHROMATICA_CSS_URL}');

html, body, .stApp {{
    font-family: "Plus Jakarta Sans", sans-serif;
}}

/* Chromatica on sidebar + descendants — !important beats Streamlit Emotion (.st-emotion-cache-*) */
{roots_ff} {{
    font-family: "Chromatica", "Plus Jakarta Sans", sans-serif !important;
}}

{sb} *:not(.sidebar-brand),
{sc} *:not(.sidebar-brand) {{
    font-family: "Chromatica", "Plus Jakarta Sans", sans-serif !important;
}}

{roots_bg} {{
    background-color: {p["sidebar_bg"]} !important;
}}

{sb} .block-container {{
    color: #ffffff !important;
}}

{sb} p:not(.sidebar-brand),
{sb} span,
{sb} label,
{sb} [data-baseweb="radio"] label,
{sb} [role="radiogroup"] label {{
    color: #ffffff !important;
}}

{sb} h1,
{sb} h2,
{sb} h3,
{sb} h4,
{sb} h5,
{sb} h6 {{
    color: #ffffff !important;
}}

{sb} input,
{sb} textarea {{
    background-color: rgba(255, 255, 255, 0.18) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.45) !important;
    caret-color: #ffffff;
}}

{sb} input::placeholder {{
    color: rgba(255, 255, 255, 0.75);
}}

/* API URL text input (key=api_base → .st-key-api_base): dark field, cream text */
{sb} .st-key-api_base input,
{sb} .st-key-api_base textarea {{
    background-color: {p["api_url_field_bg"]} !important;
    color: {p["api_url_field_fg"]} !important;
    border-color: rgba(255, 241, 229, 0.38) !important;
    caret-color: {p["api_url_field_fg"]} !important;
}}
{sb} .st-key-api_base input::placeholder {{
    color: rgba(255, 241, 229, 0.52) !important;
}}
{sb} .st-key-api_base [data-baseweb="base-input"],
{sb} .st-key-api_base [data-baseweb="input"] {{
    background-color: {p["api_url_field_bg"]} !important;
    color: {p["api_url_field_fg"]} !important;
}}

{sb} svg {{
    fill: #ffffff !important;
}}

{sb} p.sidebar-brand {{
    font-family: "Syne", sans-serif !important;
    font-weight: 800 !important;
    font-size: clamp(1.5rem, 3vw, 2rem);
    line-height: 1.0;
    color: {p["brand"]} !important;
    margin: 0 0 1rem 0 !important;
    padding: 0 !important;
    text-align: left;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: "Fraunces", Georgia, serif !important;
    color: {p["ink"]} !important;
}}

.stApp a:link {{ color: {p["link"]}; }}
.stApp a:visited {{ color: {p["link_v"]}; }}
.stApp a:hover {{ color: {p["link_h"]}; }}

div[data-testid="stButton"] button {{
    border-radius: 8px;
    font-weight: 600;
    border: none;
    transition: background-color 0.2s ease, box-shadow 0.2s ease;
}}

/* Hide sidebar expand/collapse control (Material keyboard_double_arrow_* icon flicker) */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"] {{
    display: none !important;
}}
</style>"""


def inject_plum_styles() -> None:
    st.markdown(plum_ui_css(), unsafe_allow_html=True)
