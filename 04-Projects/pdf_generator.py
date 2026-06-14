"""Generates professional PDF account statements using reportlab."""
from __future__ import annotations

from datetime import datetime
from io import BytesIO

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config.settings import BANK_NAME, BANK_TAGLINE, CURRENCY_SYMBOL


PRIMARY = colors.HexColor("#FF2D95")
SECONDARY = colors.HexColor("#00E676")
DARK = colors.HexColor("#1F1147")
GREY = colors.HexColor("#6B7280")
LIGHT = colors.HexColor("#F3F4F6")


def _fmt_money(val) -> str:
    try:
        return f"{CURRENCY_SYMBOL} {float(val):,.2f}"
    except (TypeError, ValueError):
        return f"{CURRENCY_SYMBOL} 0.00"


def generate_statement_pdf(
    customer: dict,
    transactions: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
) -> bytes:
    """Generate a polished PDF account statement and return bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        title=f"{BANK_NAME} - Account Statement",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"], textColor=DARK, fontSize=22,
        leading=26, spaceAfter=2,
    )
    tagline_style = ParagraphStyle(
        "tagline", parent=styles["Normal"], textColor=GREY, fontSize=10,
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "heading", parent=styles["Heading3"], textColor=PRIMARY, fontSize=12,
        spaceBefore=10, spaceAfter=6,
    )
    normal = ParagraphStyle(
        "normal", parent=styles["Normal"], textColor=DARK, fontSize=10,
        leading=14,
    )
    small = ParagraphStyle(
        "small", parent=styles["Normal"], textColor=GREY, fontSize=9,
        leading=12,
    )

    story = []

    # --- Header ---
    header_table = Table(
        [
            [
                Paragraph(f"<b>{BANK_NAME}</b>", title_style),
                Paragraph(
                    f"<b>Account Statement</b><br/>"
                    f"<font color='#6B7280' size='9'>Generated: "
                    f"{datetime.now().strftime('%d %b %Y, %H:%M')}</font>",
                    normal,
                ),
            ]
        ],
        colWidths=[10 * cm, 7 * cm],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LINEBELOW", (0, 0), (-1, -1), 1.2, PRIMARY),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(header_table)
    story.append(Paragraph(BANK_TAGLINE, tagline_style))

    # --- Customer Info ---
    story.append(Paragraph("Customer Information", heading_style))
    info_data = [
        ["Account Holder", str(customer.get("name", ""))],
        ["Customer ID", str(customer.get("customer_id", ""))],
        ["Email", str(customer.get("email", ""))],
        ["Phone", str(customer.get("phone", ""))],
        ["Address", str(customer.get("address", ""))],
    ]
    info_table = Table(info_data, colWidths=[4.2 * cm, 12.8 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                ("TEXTCOLOR", (0, 0), (0, -1), DARK),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ]
        )
    )
    story.append(info_table)

    # --- Statement Period + Balances ---
    story.append(Paragraph("Statement Summary", heading_style))

    if not transactions.empty:
        tx_sorted = transactions.sort_values("timestamp").reset_index(drop=True)
        first = tx_sorted.iloc[0]
        last = tx_sorted.iloc[-1]
        first_amount = float(first["amount"] or 0)
        first_bal_after = float(first["balance_after_transaction"] or 0)
        if str(first["type"]).lower() == "deposit":
            opening = first_bal_after - first_amount
        else:
            opening = first_bal_after + first_amount
        closing = float(last["balance_after_transaction"] or 0)
        total_deposits = float(
            tx_sorted[tx_sorted["type"].str.lower() == "deposit"]["amount"].sum()
        )
        total_withdrawals = float(
            tx_sorted[tx_sorted["type"].str.lower() == "withdraw"]["amount"].sum()
        )
    else:
        opening = closing = total_deposits = total_withdrawals = float(
            customer.get("balance", 0) or 0
        )
        total_deposits = 0.0
        total_withdrawals = 0.0

    summary_data = [
        ["Period", f"{start_date.strftime('%d %b %Y')}  to  {end_date.strftime('%d %b %Y')}"],
        ["Opening Balance", _fmt_money(opening)],
        ["Total Deposits", _fmt_money(total_deposits)],
        ["Total Withdrawals", _fmt_money(total_withdrawals)],
        ["Closing Balance", _fmt_money(closing)],
    ]
    summary_table = Table(summary_data, colWidths=[4.2 * cm, 12.8 * cm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (1, -1), (1, -1), SECONDARY),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ]
        )
    )
    story.append(summary_table)

    # --- Transactions Table ---
    story.append(Paragraph("Transaction History", heading_style))

    tx_header = ["Date", "Txn ID", "Type", "Reason", "Amount", "Balance"]
    tx_rows = [tx_header]

    if transactions.empty:
        tx_rows.append(["-", "-", "-", "No transactions in this period", "-", "-"])
    else:
        display = transactions.sort_values("timestamp", ascending=True).reset_index(drop=True)
        for _, row in display.iterrows():
            ts = row["timestamp"]
            ts_str = (
                ts.strftime("%d %b %Y %H:%M")
                if isinstance(ts, (pd.Timestamp, datetime))
                else str(ts)
            )
            tx_rows.append(
                [
                    ts_str,
                    str(row["transaction_id"]),
                    str(row["type"]).title(),
                    str(row["reason"] or "-")[:40],
                    _fmt_money(row["amount"]),
                    _fmt_money(row["balance_after_transaction"]),
                ]
            )

    tx_table = Table(
        tx_rows,
        colWidths=[3.1 * cm, 2.8 * cm, 1.8 * cm, 4.0 * cm, 2.6 * cm, 2.7 * cm],
        repeatRows=1,
    )
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("FONTSIZE", (0, 1), (-1, -1), 8.8),
        ("TEXTCOLOR", (0, 1), (-1, -1), DARK),
        ("ALIGN", (4, 1), (5, -1), "RIGHT"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]
    for i in range(1, len(tx_rows)):
        row_type = tx_rows[i][2].lower()
        if row_type == "deposit":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#059669")))
        elif row_type == "withdraw":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#DC2626")))
    tx_table.setStyle(TableStyle(style_cmds))
    story.append(tx_table)

    story.append(Spacer(1, 0.6 * cm))
    story.append(
        Paragraph(
            "This is a system-generated statement and does not require a signature. "
            "All amounts are in Indian Rupees unless stated otherwise.",
            small,
        )
    )
    story.append(
        Paragraph(
            f"&copy; {datetime.now().year} {BANK_NAME}. All rights reserved.",
            small,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
