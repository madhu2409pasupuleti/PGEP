"""Deposit funds page."""
from __future__ import annotations

import streamlit as st

from database import excel_db
from utils.styles import balance_card, format_currency, header_strip


def render() -> None:
    user = st.session_state.user
    customer = excel_db.get_customer_by_id(user["customer_id"])
    if not customer:
        st.error("Account not found.")
        return

    header_strip(user_name=customer["name"])
    st.markdown("### Deposit Funds")
    st.caption("Add money to your NovaTrust account.")

    left, right = st.columns([1, 1])
    with left:
        balance_card(float(customer.get("balance", 0) or 0), customer["customer_id"])

    with right:
        st.markdown('<div class="nt-card">', unsafe_allow_html=True)
        st.markdown("#### New Deposit")
        with st.form("deposit_form", clear_on_submit=True):
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                help="Enter the amount you want to deposit.",
            )
            reason = st.text_input(
                "Reason / Description",
                placeholder="e.g. Salary credit, Gift, Savings",
            )
            submit = st.form_submit_button("Deposit", use_container_width=True)

        if submit:
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            elif not reason.strip():
                st.error("Please provide a reason for this deposit.")
            else:
                try:
                    new_bal = excel_db.deposit(
                        user["customer_id"], float(amount), reason.strip()
                    )
                    st.success(
                        f"Deposited {format_currency(amount)}. "
                        f"New balance: {format_currency(new_bal)}."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Deposit failed: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)
