"""NovaTrust Bank - Streamlit entry point."""
from __future__ import annotations

import streamlit as st

from config.settings import BANK_NAME, BANK_TAGLINE
from database import excel_db
from utils.styles import inject_global_css
from views import dashboard, deposit, login, signup, statement, withdraw


st.set_page_config(
    page_title=f"{BANK_NAME} - Online Banking",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

excel_db.init_db()
inject_global_css()


def _init_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("auth_view", "login")


def _render_auth() -> None:
    if st.session_state.auth_view == "signup":
        signup.render()
    else:
        login.render()


def _render_sidebar() -> None:
    user = st.session_state.user
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 0.4rem 0 1.2rem 0;">
                <div class="nt-logo-badge" style="width:58px; height:58px; font-size:1.2rem;">NT</div>
                <h2 style="margin: 0.55rem 0 0.1rem; font-size:1.25rem;">{BANK_NAME}</h2>
                <div style="color:#BFBFBF; font-size:0.82rem;">{BANK_TAGLINE}</div>
            </div>
            <hr/>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="margin: 0.2rem 0 1rem 0;">
                <div style="color:#BFBFBF; font-size:0.78rem; letter-spacing:1px;">SIGNED IN AS</div>
                <div style="font-size:1rem; font-weight:600;">{user['name']}</div>
                <div style="color:#BFBFBF; font-size:0.82rem;">{user['email']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_items = [
            ("Dashboard", "🏠  Dashboard"),
            ("Deposit", "💰  Deposit"),
            ("Withdraw", "💸  Withdraw"),
            ("Statement", "📄  Statement"),
        ]
        for key, label in nav_items:
            active = st.session_state.page == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.button("Sign Out", key="logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "Dashboard"
            st.session_state.auth_view = "login"
            st.rerun()


def _render_page() -> None:
    page = st.session_state.page
    if page == "Dashboard":
        dashboard.render()
    elif page == "Deposit":
        deposit.render()
    elif page == "Withdraw":
        withdraw.render()
    elif page == "Statement":
        statement.render()
    else:
        dashboard.render()


def main() -> None:
    _init_state()
    if st.session_state.user is None:
        _render_auth()
    else:
        _render_sidebar()
        _render_page()


if __name__ == "__main__":
    main()
