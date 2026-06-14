"""Global CSS and UI helpers for the banking app."""
from __future__ import annotations

import streamlit as st

from config.settings import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BANK_NAME,
    CARD_BG,
    CARD_BORDER,
    CURRENCY_SYMBOL,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
)


def inject_global_css() -> None:
    """Injects the global stylesheet for the banking app."""
    css = f"""
    <style>
    /* ---- Base app ---- */
    .stApp {{
        background: linear-gradient(135deg, {BACKGROUND_COLOR} 0%, #5B2BB6 55%, #2E1065 100%);
        color: {TEXT_COLOR};
        font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif;
    }}
    .main .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }}

    /* ---- Headings ---- */
    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_COLOR} !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px;
    }}
    p, label, span, div {{
        color: {TEXT_COLOR};
    }}

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #311B6B 0%, #1F1147 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }}
    [data-testid="stSidebar"] * {{
        color: {TEXT_COLOR} !important;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {TEXT_COLOR} !important;
    }}

    /* ---- Inputs ---- */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea,
    .stDateInput input {{
        background-color: rgba(255,255,255,0.08) !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.75rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 0 2px {PRIMARY_COLOR}33 !important;
    }}
    .stTextInput label, .stNumberInput label,
    .stTextArea label, .stDateInput label,
    .stSelectbox label {{
        color: {ACCENT_COLOR} !important;
        font-weight: 500 !important;
    }}

    /* ---- Buttons ---- */
    .stButton > button, .stDownloadButton > button {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #D81B85 100%);
        color: {TEXT_COLOR} !important;
        border: 0;
        border-radius: 10px;
        padding: 0.55rem 1.2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: transform 0.08s ease, box-shadow 0.2s ease;
        box-shadow: 0 6px 20px {PRIMARY_COLOR}40;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 10px 26px {PRIMARY_COLOR}55;
        color: {TEXT_COLOR} !important;
    }}
    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* ---- Card ---- */
    .nt-card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.18);
        margin-bottom: 1rem;
    }}
    .nt-card h3 {{
        margin: 0 0 0.4rem 0;
        font-size: 1.05rem;
        color: {ACCENT_COLOR} !important;
        font-weight: 500 !important;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}
    .nt-card .value {{
        font-size: 1.55rem;
        font-weight: 700;
        color: {TEXT_COLOR};
    }}

    /* ---- Balance card ---- */
    .nt-balance {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #6D28D9 100%);
        border-radius: 18px;
        padding: 1.8rem;
        color: {TEXT_COLOR};
        box-shadow: 0 14px 36px rgba(0,0,0,0.25);
        position: relative;
        overflow: hidden;
    }}
    .nt-balance::after {{
        content: "";
        position: absolute;
        right: -40px; top: -60px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, {SECONDARY_COLOR}40 0%, transparent 70%);
        border-radius: 50%;
    }}
    .nt-balance .label {{
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.78rem;
        color: rgba(255,255,255,0.85);
    }}
    .nt-balance .amount {{
        font-size: 2.6rem;
        font-weight: 800;
        margin-top: 0.3rem;
    }}
    .nt-balance .sub {{
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: rgba(255,255,255,0.9);
    }}

    /* ---- Header strip ---- */
    .nt-header {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 1rem 1.4rem;
        background: rgba(0,0,0,0.18);
        border: 1px solid {CARD_BORDER};
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }}
    .nt-header .brand {{
        font-size: 1.25rem; font-weight: 800; letter-spacing: 0.5px;
    }}
    .nt-header .brand .dot {{
        color: {SECONDARY_COLOR};
    }}
    .nt-header .who {{
        font-size: 0.92rem; color: {ACCENT_COLOR};
    }}

    /* ---- Pills / chips ---- */
    .nt-pill {{
        display: inline-block;
        padding: 0.18rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }}
    .nt-pill.deposit {{ background: {SECONDARY_COLOR}33; color: {SECONDARY_COLOR}; }}
    .nt-pill.withdraw {{ background: {PRIMARY_COLOR}33; color: {PRIMARY_COLOR}; }}

    /* ---- Dataframes ---- */
    [data-testid="stDataFrame"] {{
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 0.4rem;
        border: 1px solid {CARD_BORDER};
    }}

    /* ---- Alerts ---- */
    .stAlert {{
        border-radius: 12px;
    }}

    /* ---- Auth shell ---- */
    .nt-auth-shell {{
        max-width: 460px;
        margin: 2rem auto;
    }}
    .nt-auth-shell .brand-block {{
        text-align: center;
        margin-bottom: 1.2rem;
    }}
    .nt-auth-shell .brand-block h1 {{
        font-size: 2rem; margin: 0.2rem 0 0.15rem;
    }}
    .nt-auth-shell .brand-block p {{
        color: {ACCENT_COLOR}; margin: 0;
    }}
    .nt-logo-badge {{
        width: 70px; height: 70px; margin: 0 auto;
        border-radius: 18px;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%);
        display: flex; align-items: center; justify-content: center;
        color: {TEXT_COLOR}; font-weight: 800; font-size: 1.6rem;
        box-shadow: 0 10px 24px rgba(0,0,0,0.25);
    }}

    /* ---- Misc ---- */
    hr {{ border-color: {CARD_BORDER} !important; }}

    /* Hide streamlit default footer/menu for cleaner banking look */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def format_currency(amount: float) -> str:
    try:
        value = float(amount or 0)
    except (TypeError, ValueError):
        value = 0.0
    return f"{CURRENCY_SYMBOL} {value:,.2f}"


def header_strip(user_name: str | None = None) -> None:
    right = f'<div class="who">Welcome, <b>{user_name}</b></div>' if user_name else ""
    st.markdown(
        f"""
        <div class="nt-header">
            <div class="brand">{BANK_NAME}<span class="dot">.</span></div>
            {right}
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="nt-card">
            <h3>{title}</h3>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def balance_card(balance: float, customer_id: str) -> None:
    st.markdown(
        f"""
        <div class="nt-balance">
            <div class="label">Available Balance</div>
            <div class="amount">{format_currency(balance)}</div>
            <div class="sub">Account ID: <b>{customer_id}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def brand_header_auth() -> None:
    st.markdown(
        f"""
        <div class="brand-block">
            <div class="nt-logo-badge">NT</div>
            <h1>{BANK_NAME}</h1>
            <p>Banking. Reimagined.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
