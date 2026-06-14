"""Password hashing and login helpers."""
from __future__ import annotations

import re

import bcrypt

from database import excel_db


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email or ""))


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone or "")
    return 7 <= len(digits) <= 15


def is_strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain a digit."
    return True, ""


def authenticate(email: str, password: str):
    customer = excel_db.get_customer_by_email(email)
    if not customer:
        return None
    if verify_password(password, str(customer.get("password", ""))):
        return customer
    return None
