
import pandas as pd


def analyze_customer_inactivity(transactions):
    """
    Estimate customer inactivity risk from transaction history.

    Risk categories are rule-based indicators, not validated
    machine-learning churn predictions.
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
                "No purchase for 31-60 days"
                if days <= 60
                else "No purchase for more than 60 days"
            )
        )
    )

    # Relative spending is used to prioritize retention actions.
    median_spend = customers["total_spend"].median()

    def recommend(row):
        high_value = row["total_spend"] >= median_spend
        risk = row["inactivity_risk"]

        if risk == "High" and high_value:
            return (
                "High Priority",
                "Personalized win-back outreach",
                "High inactivity and relatively high historical spend",
            )

        if risk == "High":
            return (
                "Re-engagement",
                "Send a re-engagement message",
                "Long time since last recorded purchase",
            )

        if risk == "Medium" and high_value:
            return (
                "Retention Priority",
                "Offer a relevant loyalty benefit",
                "Relatively high spend and increasing inactivity",
            )

        if risk == "Medium":
            return (
                "Engagement",
                "Share relevant products or offers",
                "No purchase for 31-60 days",
            )

        if high_value:
            return (
                "Loyalty Opportunity",
                "Consider a loyalty or appreciation offer",
                "Recent purchase activity and relatively high spend",
            )

        return (
            "Maintain Engagement",
            "Use regular, relevant customer communication",
            "Recent purchase activity",
        )

    recommendations = customers.apply(recommend, axis=1)

    customers[
        [
            "retention_priority",
            "recommended_action",
            "recommendation_reason",
        ]
    ] = pd.DataFrame(
        recommendations.tolist(),
        index=customers.index,
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
            "Low": "0-30 days",
            "Medium": "31-60 days",
            "High": "More than 60 days",
        },
        "spending_reference": median_spend,
    }
