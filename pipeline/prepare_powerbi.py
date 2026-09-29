import pandas as pd
from pathlib import Path

CUSTOMER_INPUT = Path("data/processed/customer_segments.parquet")
CHURN_INPUT = Path("data/processed/churn_predictions.parquet")

CUSTOMER_OUTPUT = Path(
    "data/processed/powerbi_customer_segments.parquet"
)

CHURN_OUTPUT = Path(
    "data/processed/powerbi_churn_predictions.parquet"
)

# ---------------------------------------------------------
# Customer Segmentation Dataset
# ---------------------------------------------------------

print("Loading customer segmentation data...")

customer_df = pd.read_parquet(CUSTOMER_INPUT)

customer_columns = [
    "customer_id",
    "total_spend",
    "total_transactions",
    "avg_order_value",
    "total_quantity",
    "avg_discount",
    "avg_session_duration",
    "avg_pages_viewed",
    "category_count",
    "active_months",
    "last_purchase_date",
    "days_since_last_purchase",
    "cluster",
    "customer_segment",
]

customer_segments = customer_df[customer_columns].copy()

customer_segments.to_parquet(
    CUSTOMER_OUTPUT,
    index=False,
    compression="snappy"
)

print(
    f"Customer dataset created: "
    f"{len(customer_segments):,} rows"
)

# ---------------------------------------------------------
# Churn Prediction Dataset
# ---------------------------------------------------------

print("\nLoading churn prediction data...")

churn_df = pd.read_parquet(CHURN_INPUT)

churn_columns = [
    "customer_id",
    "total_spend",
    "total_transactions",
    "avg_order_value",
    "total_quantity",
    "avg_discount",
    "avg_session_duration",
    "avg_pages_viewed",
    "category_count",
    "active_months",
    "days_since_last_purchase",
    "churned",
    "churn_probability",
    "churn_prediction",
]

churn_predictions = churn_df[churn_columns].copy()

# Create dashboard-friendly risk categories
churn_predictions["risk_level"] = pd.cut(
    churn_predictions["churn_probability"],
    bins=[-0.01, 0.30, 0.60, 1.00],
    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk",
    ],
)

churn_predictions.to_parquet(
    CHURN_OUTPUT,
    index=False,
    compression="snappy"
)

print(
    f"Churn dataset created: "
    f"{len(churn_predictions):,} rows"
)

print("\nRisk distribution:")
print(
    churn_predictions["risk_level"]
    .value_counts()
    .sort_index()
)

print("\nPower BI datasets prepared successfully.")
print(f"Customer output: {CUSTOMER_OUTPUT}")
print(f"Churn output: {CHURN_OUTPUT}")
import duckdb

SALES_INPUT = "data/processed/transactions_processed.parquet"
SALES_OUTPUT = Path(
    "data/processed/powerbi_sales_summary.parquet"
)

print("\nCreating sales analytics dataset...")

con = duckdb.connect()

sales_query = f"""
SELECT
    year,
    month,
    category,
    city,

    COUNT(*) AS transactions,

    ROUND(SUM(revenue), 2) AS revenue,

    SUM(quantity) AS quantity,

    ROUND(AVG(revenue), 2) AS average_order_value

FROM '{SALES_INPUT}'

WHERE order_status = 'Completed'

GROUP BY
    year,
    month,
    category,
    city

ORDER BY
    year,
    month,
    category,
    city
"""

sales_summary = con.execute(sales_query).fetchdf()

con.close()

sales_summary.to_parquet(
    SALES_OUTPUT,
    index=False,
    compression="snappy"
)

print(
    f"Sales dataset created: "
    f"{len(sales_summary):,} rows"
)

print("\nSales dataset columns:")
print(list(sales_summary.columns))

print("\nSample:")
print(sales_summary.head(10).to_string(index=False))

print(f"\nSales output: {SALES_OUTPUT}")