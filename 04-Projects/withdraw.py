"""Withdraw funds page."""
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
    st.markdown("### Withdraw Funds")
    st.caption("Move money out of your NovaTrust account.")

    current_balance = float(customer.get("balance", 0) or 0)

    left, right = st.columns([1, 1])
    with left:
        balance_card(current_balance, customer["customer_id"])

    with right:
        st.markdown('<div class="nt-card">', unsafe_allow_html=True)
        st.markdown("#### New Withdrawal")
        with st.form("withdraw_form", clear_on_submit=True):
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                help="Cannot exceed current balance.",
            )
            reason = st.text_input(
                "Reason / Description",
                placeholder="e.g. Rent, Groceries, Bills",
            )
            submit = st.form_submit_button("Withdraw", use_container_width=True)

        if submit:
            if amount <= 0:
                st.error("Amount must be greater than zero.")
            elif not reason.strip():
                st.error("Please provide a reason for this withdrawal.")
            elif amount > current_balance:
                st.error(
                    f"Insufficient balance. Available: {format_currency(current_balance)}."
                )
            else:
                try:
                    new_bal = excel_db.withdraw(
                        user["customer_id"], float(amount), reason.strip()
                    )
                    st.success(
                        f"Withdrew {format_currency(amount)}. "
                        f"New balance: {format_currency(new_bal)}."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Withdrawal failed: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)
