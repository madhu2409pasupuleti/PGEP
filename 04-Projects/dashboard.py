"""Dashboard page: customer info, balance and last 5 transactions."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from database import excel_db
from utils.styles import balance_card, format_currency, header_strip, info_card


def _recent_transactions_df(customer_id: str) -> pd.DataFrame:
    df = excel_db.get_customer_transactions(customer_id, limit=5)
    if df.empty:
        return df
    display = df.copy()
    display["timestamp"] = pd.to_datetime(display["timestamp"]).dt.strftime(
        "%d %b %Y, %H:%M"
    )
    display["amount"] = display["amount"].apply(format_currency)
    display["balance_after_transaction"] = display["balance_after_transaction"].apply(
        format_currency
    )
    display["type"] = display["type"].str.title()
    display = display.rename(
        columns={
            "timestamp": "Date",
            "transaction_id": "Txn ID",
            "type": "Type",
            "amount": "Amount",
            "balance_after_transaction": "Balance",
            "reason": "Reason",
        }
    )
    return display[["Date", "Txn ID", "Type", "Reason", "Amount", "Balance"]]


def render() -> None:
    user = st.session_state.user
    customer = excel_db.get_customer_by_id(user["customer_id"])
    if not customer:
        st.error("Account not found. Please sign in again.")
        st.session_state.user = None
        st.rerun()
        return

    header_strip(user_name=customer["name"])

    st.markdown("### Dashboard")
    st.caption("Your account at a glance.")

    left, right = st.columns([1.2, 1])
    with left:
        balance_card(float(customer.get("balance", 0) or 0), customer["customer_id"])
    with right:
        st.markdown(
            f"""
            <div class="nt-card" style="height:100%;">
                <h3>Account Holder</h3>
                <div class="value">{customer['name']}</div>
                <div style="color:#BFBFBF; margin-top:0.4rem;">{customer['email']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        info_card("Phone", str(customer.get("phone", "-")))
    with c2:
        info_card("Customer ID", str(customer.get("customer_id", "-")))
    with c3:
        created = str(customer.get("created_at", "-"))
        info_card("Member Since", created.split(" ")[0] if created else "-")

    st.markdown(
        f"""
        <div class="nt-card">
            <h3>Address</h3>
            <div class="value" style="font-size:1.05rem; font-weight:500;">
                {customer.get('address', '-') or '-'}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Recent Activity")
    st.caption("Last 5 transactions.")
    recent = _recent_transactions_df(user["customer_id"])
    if recent.empty:
        st.info("No transactions yet. Try a deposit from the sidebar.")
    else:
        st.dataframe(recent, use_container_width=True, hide_index=True)
