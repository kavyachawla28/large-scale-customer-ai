import duckdb

INPUT_FILE = "data/processed/transactions_processed.parquet"
OUTPUT_FILE = "data/processed/customer_features.parquet"

ANALYSIS_DATE = "2026-09-01"

print("Connecting to DuckDB...")

con = duckdb.connect()

query = f"""
SELECT
    customer_id,

    COUNT(*) AS total_transactions,

    ROUND(SUM(revenue), 2) AS total_spend,

    ROUND(AVG(revenue), 2) AS avg_order_value,

    SUM(quantity) AS total_quantity,

    ROUND(AVG(discount), 4) AS avg_discount,

    ROUND(AVG(session_duration), 2) AS avg_session_duration,

    ROUND(AVG(pages_viewed), 2) AS avg_pages_viewed,

    COUNT(DISTINCT category) AS category_count,

    COUNT(DISTINCT DATE_TRUNC('month', timestamp)) AS active_months,

    MAX(timestamp) AS last_purchase_date,

    DATE_DIFF(
        'day',
        CAST(MAX(timestamp) AS DATE),
        DATE '{ANALYSIS_DATE}'
    ) AS days_since_last_purchase

FROM '{INPUT_FILE}'

WHERE order_status = 'Completed'
  AND CAST(timestamp AS DATE) <= DATE '{ANALYSIS_DATE}'

GROUP BY customer_id
"""

print("Creating customer-level features...")

customer_features = con.execute(query).fetchdf()

print("\nCustomer feature table created.")
print(f"Rows: {len(customer_features):,}")
print(f"Columns: {len(customer_features.columns)}")

print("\nFeature columns:")
print(list(customer_features.columns))

print("\nSample:")
print(customer_features.head(10).to_string(index=False))

customer_features.to_parquet(
    OUTPUT_FILE,
    index=False,
    compression="snappy"
)

con.close()

print(f"\nOutput: {OUTPUT_FILE}")