# NovaTrust Bank — Streamlit Banking Web App

A full-featured banking web application built with **Streamlit + Python**, using an **Excel (.xlsx) file as the database** (pandas + openpyxl). Includes authentication with bcrypt, deposit / withdraw, account statements, and professional PDF exports via reportlab.

---

## Project Structure

```
BC-BankApp/
│
├── app.py                      # Streamlit entry point
├── requirements.txt            # Python dependencies
├── README.md
│
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Bank name, colors, paths, constants
│
├── database/
│   ├── __init__.py
│   ├── excel_db.py             # Excel read / write data layer
│   └── bank_db.xlsx            # Auto-created on first launch (customers + transactions)
│
├── utils/
│   ├── __init__.py
│   ├── auth.py                 # bcrypt hashing, validation, login
│   ├── pdf_generator.py        # reportlab PDF statement builder
│   └── styles.py               # Global CSS + UI helpers (cards, header, balance)
│
├── views/
│   ├── __init__.py
│   ├── login.py                # Login page
│   ├── signup.py               # Create account page
│   ├── dashboard.py            # Dashboard (profile, balance, recent txns)
│   ├── deposit.py              # Deposit funds
│   ├── withdraw.py             # Withdraw funds
│   └── statement.py            # Statement + CSV / PDF export
│
└── assets/                     # (optional) static assets / logos
```

---

## Excel Database Structure

The file `database/bank_db.xlsx` is created automatically on first launch with two sheets.

### Sheet: `customers`
| customer_id | name | email | password | address | phone | balance | created_at |
|---|---|---|---|---|---|---|---|
| NTB100001 | John Doe | john@x.com | `<bcrypt_hash>` | ... | ... | 0.00 | 2026-04-18 10:02:33 |

### Sheet: `transactions`
| transaction_id | customer_id | type | amount | balance_after_transaction | reason | timestamp |
|---|---|---|---|---|---|---|
| TX1A2B3C4D5E | NTB100001 | deposit | 500.00 | 500.00 | Salary | 2026-04-18 10:05:12 |

- Passwords are **bcrypt hashed** — never stored in plain text.
- `customer_id` is auto-generated (`NTB100001`, `NTB100002`, ...).
- All writes reload the workbook from disk first and are serialized with a lock to prevent concurrent-overwrite issues. Writes go to a `.tmp` file and are atomically renamed.

---

## Features

- **Modern banking UI** — gradient background, glassmorphic cards, sidebar navigation, custom fonts & colors
  - Primary `#FF2D95`, Secondary `#00E676`, Accent `#BFBFBF`, Background `#8A5CF6`, Text `#FFFFFF`
- **Authentication** — login, sign-up, session-based state, bcrypt password hashing
- **Dashboard** — name, email, address, phone, balance, last 5 transactions
- **Deposit / Withdraw** — with reason, live balance validation, transaction logging
- **Account Statement** — date-range filter, type filter, summary metrics, CSV + PDF export
- **PDF Export** — branded statement with customer info, period, opening & closing balance, color-coded transaction table

---

## Setup

### 1. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

The first launch auto-creates `database/bank_db.xlsx` with empty `customers` and `transactions` sheets. The app opens at http://localhost:8501.

---

## First-Run Walkthrough

1. Click **Create an account** on the login screen.
2. Fill in your details (password must be 8+ chars with upper, lower, digit).
3. Sign in with your new email / password.
4. On the **Dashboard**, view your profile + balance (starts at `Rs. 0.00`).
5. Use **Deposit** in the sidebar to add funds.
6. Use **Withdraw** to take money out (blocked if balance is insufficient).
7. Open **Statement**, pick a date range, and download **CSV** or **PDF**.

---

## Key Implementation Notes

- **Atomic writes:** [database/excel_db.py](database/excel_db.py) writes to `bank_db.xlsx.tmp` then `os.replace()` — so a crashed write never corrupts the file.
- **Lock:** a module-level `threading.Lock` prevents concurrent writes within a single Streamlit process.
- **Reload before write:** every mutating op reloads the workbook first, so stale in-memory state can't overwrite a committed change from another tab.
- **Validation:** email regex, phone length, strong password, positive amounts, balance check on withdrawal.
- **Theming:** [utils/styles.py](utils/styles.py) injects a full CSS stylesheet so the UI does NOT look like a default Streamlit app.

---

## Customizing

- **Bank name, tagline, currency** — edit [config/settings.py](config/settings.py).
- **Colors** — update color constants in `config/settings.py` *and* `.streamlit/config.toml` (Streamlit base theme) *and* `utils/styles.py` if you want the CSS to re-derive from them.
- **PDF layout** — edit [utils/pdf_generator.py](utils/pdf_generator.py).

---

## Dependencies

- `streamlit` — web UI
- `pandas` + `openpyxl` — Excel I/O
- `bcrypt` — password hashing
- `reportlab` — PDF generation
