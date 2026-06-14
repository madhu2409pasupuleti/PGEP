"""Signup / create account page."""
from __future__ import annotations

import streamlit as st

from database import excel_db
from utils import auth
from utils.styles import brand_header_auth


def render() -> None:
    st.markdown('<div class="nt-auth-shell">', unsafe_allow_html=True)
    brand_header_auth()
    st.markdown('<div class="nt-card">', unsafe_allow_html=True)
    st.subheader("Open a new account")
    st.caption("Takes less than a minute. No paperwork required.")

    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email address", placeholder="you@example.com")
        phone = st.text_input("Phone number", placeholder="+91 98765 43210")
        address = st.text_area("Address", placeholder="Street, City, State, Country")
        password = st.text_input("Password", type="password", help="Min 8 chars, 1 upper, 1 lower, 1 digit")
        confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Create Account", use_container_width=True)

    if submit:
        errors = []
        if not all([name, email, phone, address, password, confirm]):
            errors.append("All fields are required.")
        if email and not auth.is_valid_email(email):
            errors.append("Enter a valid email address.")
        if phone and not auth.is_valid_phone(phone):
            errors.append("Enter a valid phone number.")
        if password and confirm and password != confirm:
            errors.append("Passwords do not match.")
        if password:
            ok, msg = auth.is_strong_password(password)
            if not ok:
                errors.append(msg)

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                if excel_db.customer_exists(email.strip()):
                    st.error("An account with this email already exists.")
                else:
                    hashed = auth.hash_password(password)
                    cid = excel_db.create_customer(
                        name=name.strip(),
                        email=email.strip(),
                        hashed_password=hashed,
                        address=address.strip(),
                        phone=phone.strip(),
                    )
                    st.success(
                        f"Account created! Your Customer ID is {cid}. Please sign in."
                    )
                    st.session_state.auth_view = "login"
                    st.rerun()
            except Exception as exc:
                st.error(f"Could not create account: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption("Already have an account?")
    with col2:
        if st.button("Sign in", key="go_login", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
