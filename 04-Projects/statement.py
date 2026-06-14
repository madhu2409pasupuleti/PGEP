"""Account statement page with date range filter and PDF export."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

from database import excel_db
from utils.pdf_generator import generate_statement_pdf
from utils.styles import format_currency, header_strip


def _format_for_display(df: pd.DataFrame) -> pd.DataFrame:
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
        st.error("Account not found.")
        return

    header_strip(user_name=customer["name"])
    st.markdown("### Account Statement")
    st.caption("Filter your transaction history and export a PDF.")

    st.markdown('<div class="nt-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    default_start = date.today() - timedelta(days=30)
    default_end = date.today()
    with c1:
        start = st.date_input("From", value=default_start, key="stmt_start")
    with c2:
        end = st.date_input("To", value=default_end, key="stmt_end")
    with c3:
        tx_type = st.selectbox("Type", ["All", "Deposit", "Withdraw"], key="stmt_type")
    st.markdown("</div>", unsafe_allow_html=True)

    if start > end:
        st.error("Start date must be before or equal to end date.")
        return

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.min.time())

    df = excel_db.get_customer_transactions(
        user["customer_id"], start_date=start_dt, end_date=end_dt
    )
    if tx_type != "All" and not df.empty:
        df = df[df["type"].str.lower() == tx_type.lower()].reset_index(drop=True)

    # Summary metrics
    total_dep = float(df[df["type"].str.lower() == "deposit"]["amount"].sum()) if not df.empty else 0.0
    total_wd = float(df[df["type"].str.lower() == "withdraw"]["amount"].sum()) if not df.empty else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""<div class="nt-card"><h3>Transactions</h3>
            <div class="value">{len(df)}</div></div>""",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""<div class="nt-card"><h3>Total Deposits</h3>
            <div class="value">{format_currency(total_dep)}</div></div>""",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""<div class="nt-card"><h3>Total Withdrawals</h3>
            <div class="value">{format_currency(total_wd)}</div></div>""",
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""<div class="nt-card"><h3>Net Change</h3>
            <div class="value">{format_currency(total_dep - total_wd)}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("#### Transactions")
    display = _format_for_display(df)
    if display.empty:
        st.info("No transactions found in the selected range.")
    else:
        st.dataframe(display, use_container_width=True, hide_index=True)

    colL, colR = st.columns([1, 1])
    with colL:
        if not df.empty:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                csv_bytes,
                file_name=f"statement_{customer['customer_id']}_{start}_{end}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with colR:
        try:
            pdf_bytes = generate_statement_pdf(customer, df, start_dt, end_dt)
            st.download_button(
                "Download PDF Statement",
                pdf_bytes,
                file_name=f"statement_{customer['customer_id']}_{start}_{end}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"Could not generate PDF: {exc}")
