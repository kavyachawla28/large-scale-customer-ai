
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


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


def build_customer_features(transactions):
    """Create one behavioral feature row per customer."""

    df = transactions.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    for column in [
        "quantity",
        "discount",
        "revenue",
        "session_duration",
        "pages_viewed",
    ]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=["customer_id", "timestamp", "revenue"]
    )

    if df.empty:
        return pd.DataFrame()

    reference_date = df["timestamp"].max().normalize()

    features = (
        df.groupby("customer_id")
        .agg(
            total_spend=("revenue", "sum"),
            total_transactions=("transaction_id", "nunique"),
            avg_order_value=("revenue", "mean"),
            total_quantity=("quantity", "sum"),
            avg_discount=("discount", "mean"),
            avg_session_duration=("session_duration", "mean"),
            avg_pages_viewed=("pages_viewed", "mean"),
            category_count=("category", "nunique"),
            active_months=(
                "timestamp",
                lambda x: x.dt.to_period("M").nunique(),
            ),
            last_purchase=("timestamp", "max"),
        )
        .reset_index()
    )

    features["days_since_last_purchase"] = (
        reference_date - features["last_purchase"].dt.normalize()
    ).dt.days.clip(lower=0)

    features = features.drop(columns=["last_purchase"])

    for column in FEATURES:
        features[column] = pd.to_numeric(
            features[column], errors="coerce"
        )

    features[FEATURES] = features[FEATURES].fillna(0)

    return features


def assign_segment_labels(customer_features):
    """Name clusters using their relative spending and activity."""

    summary = (
        customer_features.groupby("cluster")
        .agg(
            spend=("total_spend", "mean"),
            activity=("total_transactions", "mean"),
            recency=("days_since_last_purchase", "mean"),
        )
    )

    spend_median = summary["spend"].median()
    activity_median = summary["activity"].median()

    labels = {}

    for cluster_id, row in summary.iterrows():
        high_spend = row["spend"] >= spend_median
        high_activity = row["activity"] >= activity_median

        if high_spend and high_activity:
            label = "High-Value Engaged"
        elif high_spend:
            label = "High-Value Infrequent"
        elif high_activity:
            label = "Regular Customers"
        else:
            label = "Low-Engagement"

        labels[cluster_id] = label

    # Prevent repeated names when cluster profiles overlap.
    used = set()
    for cluster_id in sorted(labels):
        label = labels[cluster_id]
        if label in used:
            labels[cluster_id] = f"{label} (Cluster {cluster_id})"
        used.add(labels[cluster_id])

    return labels


def segment_uploaded_customers(transactions):
    """Return customer features with K-Means segment assignments."""

    features = build_customer_features(transactions)

    if features.empty:
        return {
            "success": False,
            "error": "No valid customer records were found.",
        }

    customer_count = len(features)

    if customer_count < 4:
        return {
            "success": False,
            "error": (
                "At least 4 unique customers are required for "
                "4-cluster segmentation. Your dataset has "
                f"{customer_count}."
            ),
        }

    X = features[FEATURES].replace(
        [float("inf"), float("-inf")], 0
    ).fillna(0)

    # Constant features do not provide useful clustering information.
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(
        n_clusters=min(4, customer_count),
        random_state=42,
        n_init=10,
    )

    features["cluster"] = model.fit_predict(X_scaled)

    labels = assign_segment_labels(features)
    features["customer_segment"] = features["cluster"].map(labels)

    return {
        "success": True,
        "customers": features,
        "features_used": FEATURES,
        "clusters": features["cluster"].nunique(),
    }
