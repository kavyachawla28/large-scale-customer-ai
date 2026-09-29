import numpy as np
import pandas as pd
from pathlib import Path


# ============================================
# CONFIGURATION
# ============================================

NUM_TRANSACTIONS = 10_000
NUM_CUSTOMERS = 1_000
NUM_PRODUCTS = 500

OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "transactions_test.parquet"


# ============================================
# REPRODUCIBILITY
# ============================================

np.random.seed(42)


# ============================================
# REFERENCE DATA
# ============================================

categories = [
    "Electronics",
    "Clothing",
    "Home",
    "Beauty",
    "Sports",
    "Books",
    "Grocery",
    "Automotive",
]

devices = [
    "Mobile",
    "Desktop",
    "Tablet",
]

cities = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Jaipur",
    "Gurgaon",
    "Noida",
    "Kolkata",
]

payment_methods = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Wallet",
]

order_statuses = [
    "Completed",
    "Completed",
    "Completed",
    "Completed",
    "Cancelled",
    "Returned",
]


# ============================================
# GENERATE TRANSACTIONS
# ============================================

print(f"Generating {NUM_TRANSACTIONS:,} transactions...")

transaction_ids = np.arange(1, NUM_TRANSACTIONS + 1)

customer_ids = np.random.randint(
    1,
    NUM_CUSTOMERS + 1,
    size=NUM_TRANSACTIONS
)

product_ids = np.random.randint(
    1,
    NUM_PRODUCTS + 1,
    size=NUM_TRANSACTIONS
)

timestamps = pd.to_datetime(
    np.random.randint(
        pd.Timestamp("2024-01-01").value // 10**9,
        pd.Timestamp("2026-09-01").value // 10**9,
        size=NUM_TRANSACTIONS,
    ),
    unit="s",
)

category = np.random.choice(
    categories,
    size=NUM_TRANSACTIONS
)

quantity = np.random.randint(
    1,
    6,
    size=NUM_TRANSACTIONS
)

price = np.round(
    np.random.uniform(100, 50_000, size=NUM_TRANSACTIONS),
    2
)

discount = np.round(
    np.random.uniform(0, 0.30, size=NUM_TRANSACTIONS),
    2
)

revenue = np.round(
    quantity * price * (1 - discount),
    2
)

device = np.random.choice(
    devices,
    size=NUM_TRANSACTIONS
)

city = np.random.choice(
    cities,
    size=NUM_TRANSACTIONS
)

payment_method = np.random.choice(
    payment_methods,
    size=NUM_TRANSACTIONS
)

session_duration = np.round(
    np.random.uniform(1, 60, size=NUM_TRANSACTIONS),
    2
)

pages_viewed = np.random.randint(
    1,
    25,
    size=NUM_TRANSACTIONS
)

order_status = np.random.choice(
    order_statuses,
    size=NUM_TRANSACTIONS
)


# ============================================
# CREATE DATAFRAME
# ============================================

df = pd.DataFrame(
    {
        "transaction_id": transaction_ids,
        "customer_id": customer_ids,
        "timestamp": timestamps,
        "product_id": product_ids,
        "category": category,
        "quantity": quantity,
        "price": price,
        "discount": discount,
        "revenue": revenue,
        "device": device,
        "city": city,
        "payment_method": payment_method,
        "session_duration": session_duration,
        "pages_viewed": pages_viewed,
        "order_status": order_status,
    }
)


# ============================================
# SAVE AS PARQUET
# ============================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

df.to_parquet(
    OUTPUT_FILE,
    index=False
)


# ============================================
# SUMMARY
# ============================================

print("\nData generation completed.")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Output: {OUTPUT_FILE}")
print(f"File size: {OUTPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB")