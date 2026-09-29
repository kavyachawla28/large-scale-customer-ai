import duckdb

SQL_FILE = "sql/sales_analysis.sql"

print("Connecting to DuckDB...")

con = duckdb.connect()

with open(SQL_FILE, "r") as file:
    sql = file.read()

queries = [
    query.strip()
    for query in sql.split(";")
    if query.strip()
]

for i, query in enumerate(queries, start=1):
    print(f"\n{'=' * 60}")
    print(f"QUERY {i}")
    print("=" * 60)

    result = con.execute(query).fetchdf()
    print(result.to_string(index=False))

con.close()

print("\nDuckDB analytics completed.")