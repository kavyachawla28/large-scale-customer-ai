import polars as pl
from pathlib import Path


# ============================================
# CONFIGURATION
# ============================================

INPUT_FILE = Path("data/raw/transactions_1000000.parquet")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "transactions_processed.parquet"


# ============================================
# READ RAW PARQUET
# ============================================

print("Reading raw transaction data...")

df = pl.read_parquet(INPUT_FILE)

print(f"Raw shape: {df.shape}")


# ============================================
# DATA QUALITY CHECK
# ============================================

print("\nChecking for null values...")

null_counts = df.null_count()

print(null_counts)


# ============================================
# DATA CLEANING
# ============================================

print("\nCleaning transaction data...")

df = df.filter(
    pl.col("quantity") > 0
)

df = df.filter(
    pl.col("price") > 0
)

df = df.filter(
    pl.col("revenue") > 0
)


# ============================================
# FEATURE CREATION
# ============================================

print("Creating derived columns...")

df = df.with_columns(
    [
        pl.col("timestamp").dt.year().alias("year"),

        pl.col("timestamp").dt.month().alias("month"),

        pl.col("timestamp").dt.date().alias("transaction_date"),

        (
            pl.col("quantity") * pl.col("price")
        ).alias("gross_amount"),

        (
            pl.col("quantity")
            * pl.col("price")
            * pl.col("discount")
        ).alias("discount_amount"),

        (
            pl.col("revenue")
            / pl.col("quantity")
        ).alias("revenue_per_item"),
    ]
)


# ============================================
# WRITE PROCESSED PARQUET
# ============================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

df.write_parquet(
    OUTPUT_FILE,
    compression="snappy",
)


# ============================================
# SUMMARY
# ============================================

print("\nTransformation completed.")

print(f"Processed shape: {df.shape}")

print(f"Output: {OUTPUT_FILE}")

print(
    f"Output size: "
    f"{OUTPUT_FILE.stat().st_size / (1024 * 1024):.2f} MB"
)