
import pandas as pd


def analyze_customer_inactivity(transactions):
    """
    Estimate customer inactivity risk from transaction history.

    This is a rule-based estimate, not a trained or validated
    machine-learning churn prediction model.
    """

    required_columns = {
        "customer_id",
        "transaction_id",
        "timestamp",
        "revenue",
    }

    missing = required_columns.difference(transactions.columns)

    if missing:
        return {
            "success": False,
            "error": (
                "Missing required columns: "
                + ", ".join(sorted(missing))
            ),
        }

    df = transactions.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )
    df["revenue"] = pd.to_numeric(
        df["revenue"], errors="coerce"
    )

    df = df.dropna(
        subset=["customer_id", "transaction_id", "timestamp"]
    )

    if df.empty:
        return {
            "success": False,
            "error": "No valid customer transaction history was found.",
        }

    # Use the latest date in the uploaded data as the reference date.
    # This avoids comparing historical datasets against today's date.
    reference_date = df["timestamp"].max().normalize()

    customers = (
        df.groupby("customer_id")
        .agg(
            last_purchase=("timestamp", "max"),
            total_transactions=("transaction_id", "nunique"),
            total_spend=("revenue", "sum"),
        )
        .reset_index()
    )

    customers["days_since_last_purchase"] = (
        reference_date - customers["last_purchase"].dt.normalize()
    ).dt.days.clip(lower=0)

    # Transparent heuristic thresholds, not learned model boundaries.
    customers["inactivity_risk"] = pd.cut(
        customers["days_since_last_purchase"],
        bins=[-1, 30, 60, float("inf")],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    customers["risk_reason"] = customers[
        "days_since_last_purchase"
    ].map(
        lambda days: (
            "Purchased within the last 30 days"
            if days <= 30
            else (
                "No purchase for 31–60 days"
                if days <= 60
                else "No purchase for more than 60 days"
            )
        )
    )

    customers = customers.sort_values(
        ["days_since_last_purchase", "total_spend"],
        ascending=[False, False],
    ).reset_index(drop=True)

    return {
        "success": True,
        "customers": customers,
        "reference_date": reference_date,
        "risk_thresholds_days": {
            "Low": "0–30 days",
            "Medium": "31–60 days",
            "High": "More than 60 days",
        },
    }
