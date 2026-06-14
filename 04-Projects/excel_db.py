"""Excel-backed database layer for the bank application.

All read/write operations reload the workbook from disk to avoid stale-state
issues when multiple actions occur in the same session.
"""
from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime
from typing import Optional

import pandas as pd

from config.settings import (
    CUSTOMERS_SHEET,
    DB_DIR,
    DB_FILE,
    TRANSACTIONS_SHEET,
)

_LOCK = threading.Lock()

CUSTOMER_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "password",
    "address",
    "phone",
    "balance",
    "created_at",
]

TRANSACTION_COLUMNS = [
    "transaction_id",
    "customer_id",
    "type",
    "amount",
    "balance_after_transaction",
    "reason",
    "timestamp",
]


def _ensure_dir() -> None:
    os.makedirs(DB_DIR, exist_ok=True)


def init_db() -> None:
    """Create the Excel workbook with empty sheets if it doesn't exist."""
    _ensure_dir()
    if os.path.exists(DB_FILE):
        return
    customers = pd.DataFrame(columns=CUSTOMER_COLUMNS)
    transactions = pd.DataFrame(columns=TRANSACTION_COLUMNS)
    with pd.ExcelWriter(DB_FILE, engine="openpyxl") as writer:
        customers.to_excel(writer, sheet_name=CUSTOMERS_SHEET, index=False)
        transactions.to_excel(writer, sheet_name=TRANSACTIONS_SHEET, index=False)


def _read_sheet(sheet_name: str, columns: list[str]) -> pd.DataFrame:
    try:
        df = pd.read_excel(DB_FILE, sheet_name=sheet_name, engine="openpyxl")
    except (FileNotFoundError, ValueError):
        init_db()
        df = pd.read_excel(DB_FILE, sheet_name=sheet_name, engine="openpyxl")
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns]


def read_customers() -> pd.DataFrame:
    with _LOCK:
        return _read_sheet(CUSTOMERS_SHEET, CUSTOMER_COLUMNS)


def read_transactions() -> pd.DataFrame:
    with _LOCK:
        return _read_sheet(TRANSACTIONS_SHEET, TRANSACTION_COLUMNS)


def _write_all(customers: pd.DataFrame, transactions: pd.DataFrame) -> None:
    _ensure_dir()
    tmp_file = DB_FILE + ".tmp.xlsx"
    with pd.ExcelWriter(tmp_file, engine="openpyxl") as writer:
        customers.to_excel(writer, sheet_name=CUSTOMERS_SHEET, index=False)
        transactions.to_excel(writer, sheet_name=TRANSACTIONS_SHEET, index=False)
    os.replace(tmp_file, DB_FILE)


def _generate_customer_id(existing: pd.DataFrame) -> str:
    prefix = "NTB"
    if existing.empty:
        return f"{prefix}100001"
    existing_ids = existing["customer_id"].astype(str).tolist()
    nums = []
    for cid in existing_ids:
        try:
            nums.append(int(cid.replace(prefix, "")))
        except (ValueError, AttributeError):
            continue
    next_num = max(nums) + 1 if nums else 100001
    return f"{prefix}{next_num}"


def customer_exists(email: str) -> bool:
    df = read_customers()
    if df.empty:
        return False
    return (df["email"].str.lower() == email.lower()).any()


def create_customer(
    name: str,
    email: str,
    hashed_password: str,
    address: str,
    phone: str,
) -> str:
    """Create a new customer and return the new customer_id."""
    with _LOCK:
        customers = _read_sheet(CUSTOMERS_SHEET, CUSTOMER_COLUMNS)
        transactions = _read_sheet(TRANSACTIONS_SHEET, TRANSACTION_COLUMNS)

        if not customers.empty and (customers["email"].str.lower() == email.lower()).any():
            raise ValueError("An account with this email already exists.")

        customer_id = _generate_customer_id(customers)
        new_row = {
            "customer_id": customer_id,
            "name": name,
            "email": email,
            "password": hashed_password,
            "address": address,
            "phone": phone,
            "balance": 0.0,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        customers = pd.concat([customers, pd.DataFrame([new_row])], ignore_index=True)
        _write_all(customers, transactions)
        return customer_id


def get_customer_by_email(email: str) -> Optional[dict]:
    df = read_customers()
    if df.empty:
        return None
    match = df[df["email"].str.lower() == email.lower()]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_customer_by_id(customer_id: str) -> Optional[dict]:
    df = read_customers()
    if df.empty:
        return None
    match = df[df["customer_id"] == customer_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def _append_transaction(
    transactions: pd.DataFrame,
    customer_id: str,
    tx_type: str,
    amount: float,
    balance_after: float,
    reason: str,
) -> pd.DataFrame:
    new_tx = {
        "transaction_id": f"TX{uuid.uuid4().hex[:10].upper()}",
        "customer_id": customer_id,
        "type": tx_type,
        "amount": round(float(amount), 2),
        "balance_after_transaction": round(float(balance_after), 2),
        "reason": reason,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return pd.concat([transactions, pd.DataFrame([new_tx])], ignore_index=True)


def deposit(customer_id: str, amount: float, reason: str) -> float:
    """Deposit funds and return the new balance."""
    if amount <= 0:
        raise ValueError("Deposit amount must be positive.")

    with _LOCK:
        customers = _read_sheet(CUSTOMERS_SHEET, CUSTOMER_COLUMNS)
        transactions = _read_sheet(TRANSACTIONS_SHEET, TRANSACTION_COLUMNS)

        idx_match = customers.index[customers["customer_id"] == customer_id]
        if len(idx_match) == 0:
            raise ValueError("Customer not found.")
        idx = idx_match[0]

        current = float(customers.at[idx, "balance"] or 0)
        new_balance = round(current + float(amount), 2)
        customers.at[idx, "balance"] = new_balance

        transactions = _append_transaction(
            transactions, customer_id, "deposit", amount, new_balance, reason
        )
        _write_all(customers, transactions)
        return new_balance


def withdraw(customer_id: str, amount: float, reason: str) -> float:
    """Withdraw funds and return the new balance."""
    if amount <= 0:
        raise ValueError("Withdrawal amount must be positive.")

    with _LOCK:
        customers = _read_sheet(CUSTOMERS_SHEET, CUSTOMER_COLUMNS)
        transactions = _read_sheet(TRANSACTIONS_SHEET, TRANSACTION_COLUMNS)

        idx_match = customers.index[customers["customer_id"] == customer_id]
        if len(idx_match) == 0:
            raise ValueError("Customer not found.")
        idx = idx_match[0]

        current = float(customers.at[idx, "balance"] or 0)
        if float(amount) > current:
            raise ValueError("Insufficient balance for this withdrawal.")

        new_balance = round(current - float(amount), 2)
        customers.at[idx, "balance"] = new_balance

        transactions = _append_transaction(
            transactions, customer_id, "withdraw", amount, new_balance, reason
        )
        _write_all(customers, transactions)
        return new_balance


def get_customer_transactions(
    customer_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    df = read_transactions()
    if df.empty:
        return df

    df = df[df["customer_id"] == customer_id].copy()
    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp", ascending=False)

    if start_date is not None:
        df = df[df["timestamp"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        end = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df = df[df["timestamp"] <= end]

    if limit:
        df = df.head(limit)
    return df.reset_index(drop=True)
