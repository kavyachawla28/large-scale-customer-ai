import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

INPUT_FILE = "data/processed/customer_features.parquet"
OUTPUT_FILE = "data/processed/customer_segments.parquet"

print("Loading customer features...")

df = pd.read_parquet(INPUT_FILE)

print(f"Customers: {len(df):,}")
print(f"Features available: {len(df.columns)}")

FEATURES = [
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
]

print("\nSelected ML features:")

for feature in FEATURES:
    print(f"- {feature}")

X = df[FEATURES].copy()

print("\nScaling features...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"Scaled matrix shape: {X_scaled.shape}")

print("\nTraining K-Means...")

model = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

df["cluster"] = model.fit_predict(X_scaled)

print("\nCluster distribution:")
print(df["cluster"].value_counts().sort_index())

# Business interpretation of discovered clusters
segment_labels = {
    0: "High-Value Engaged",
    1: "Regular Customers",
    2: "Low-Engagement",
    3: "High-Value Infrequent",
}

df["customer_segment"] = df["cluster"].map(segment_labels)

print("\nSegment distribution:")
print(df["customer_segment"].value_counts())

# Display cluster behavior for validation
print("\nCluster behavior summary:")

summary = (
    df.groupby(["cluster", "customer_segment"])[FEATURES]
    .mean()
    .round(2)
)

print(summary.to_string())

# Save results
df.to_parquet(
    OUTPUT_FILE,
    index=False,
    compression="snappy"
)

print("\nSegmentation completed.")
print(f"Output: {OUTPUT_FILE}")