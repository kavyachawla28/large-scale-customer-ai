import duckdb

print("Connecting to DuckDB...")

con = duckdb.connect()

result = con.execute("""
    SELECT
        COUNT(*) AS total_transactions,
        SUM(revenue) AS total_revenue,
        AVG(revenue) AS average_transaction_value
    FROM 'data/processed/transactions_processed.parquet'
""").fetchone()

print("\nAnalytics Result:")
print(f"Total transactions: {result[0]:,}")
print(f"Total revenue: ₹{result[1]:,.2f}")
print(f"Average transaction value: ₹{result[2]:,.2f}")

con.close()