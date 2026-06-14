"""Login page."""
from __future__ import annotations

import streamlit as st

from utils import auth
from utils.styles import brand_header_auth


def render() -> None:
    st.markdown('<div class="nt-auth-shell">', unsafe_allow_html=True)
    brand_header_auth()
    st.markdown('<div class="nt-card">', unsafe_allow_html=True)
    st.subheader("Sign in to your account")
    st.caption("Access your personal banking dashboard securely.")

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Sign In", use_container_width=True)

    if submit:
        if not email or not password:
            st.error("Please enter both email and password.")
        elif not auth.is_valid_email(email):
            st.error("Enter a valid email address.")
        else:
            customer = auth.authenticate(email.strip(), password)
            if customer is None:
                st.error("Invalid email or password.")
            else:
                st.session_state.user = {
                    "customer_id": customer["customer_id"],
                    "name": customer["name"],
                    "email": customer["email"],
                }
                st.session_state.page = "Dashboard"
                st.success(f"Welcome back, {customer['name']}!")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption("New to NovaTrust?")
    with col2:
        if st.button("Create an account", key="go_signup", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
