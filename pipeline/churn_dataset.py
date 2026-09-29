import duckdb

INPUT_FILE = "data/processed/transactions_processed.parquet"
OUTPUT_FILE = "data/processed/churn_dataset.parquet"

CUTOFF_DATE = "2026-06-01"
CHURN_END_DATE = "2026-09-01"

print("Connecting to DuckDB...")

con = duckdb.connect()

query = f"""
WITH historical_features AS (

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
            DATE '{CUTOFF_DATE}'
        ) AS days_since_last_purchase

    FROM '{INPUT_FILE}'

    WHERE order_status = 'Completed'
      AND CAST(timestamp AS DATE) < DATE '{CUTOFF_DATE}'

    GROUP BY customer_id
),

future_activity AS (

    SELECT DISTINCT customer_id

    FROM '{INPUT_FILE}'

    WHERE order_status = 'Completed'
      AND CAST(timestamp AS DATE) >= DATE '{CUTOFF_DATE}'
      AND CAST(timestamp AS DATE) < DATE '{CHURN_END_DATE}'
)

SELECT
    h.*,

    CASE
        WHEN f.customer_id IS NULL THEN 1
        ELSE 0
    END AS churned

FROM historical_features h

LEFT JOIN future_activity f
    ON h.customer_id = f.customer_id
"""

print("Creating leakage-free churn dataset...")

churn_dataset = con.execute(query).fetchdf()

print("\nChurn dataset created.")
print(f"Rows: {len(churn_dataset):,}")
print(f"Columns: {len(churn_dataset.columns)}")

print("\nChurn distribution:")
print(churn_dataset["churned"].value_counts().sort_index())

print("\nSample:")
print(churn_dataset.head(10).to_string(index=False))

churn_dataset.to_parquet(
    OUTPUT_FILE,
    index=False,
    compression="snappy"
)

con.close()

print(f"\nOutput: {OUTPUT_FILE}")