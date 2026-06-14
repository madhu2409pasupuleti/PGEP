"""Application configuration."""
import os

BANK_NAME = "NovaTrust Bank"
BANK_TAGLINE = "Banking. Reimagined."
BANK_SLOGAN = "Secure. Smart. Seamless."

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_FILE = os.path.join(DB_DIR, "bank_db.xlsx")

CUSTOMERS_SHEET = "customers"
TRANSACTIONS_SHEET = "transactions"

PRIMARY_COLOR = "#FF2D95"
SECONDARY_COLOR = "#00E676"
ACCENT_COLOR = "#BFBFBF"
BACKGROUND_COLOR = "#8A5CF6"
TEXT_COLOR = "#FFFFFF"
CARD_BG = "rgba(255, 255, 255, 0.10)"
CARD_BORDER = "rgba(255, 255, 255, 0.20)"

CURRENCY = "INR"
CURRENCY_SYMBOL = "Rs."
