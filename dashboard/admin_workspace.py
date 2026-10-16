
from pathlib import Path

import polars as pl
import pandas as pd
import plotly.express as px
import streamlit as st

from models.uploaded_data_analytics import segment_uploaded_customers
from models.uploaded_churn_risk import analyze_customer_inactivity


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_ROOT = PROJECT_ROOT / "data" / "user_uploads"

REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_id",
    "timestamp",
    "product_id",
    "category",
    "quantity",
    "price",
    "discount",
    "revenue",
    "device",
    "city",
    "payment_method",
    "session_duration",
    "pages_viewed",
    "order_status",
]


def read_uploaded_file(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pl.read_csv(uploaded_file)

    if filename.endswith(".parquet"):
        return pl.read_parquet(uploaded_file)

    raise ValueError("Only CSV and Parquet files are supported.")


def validate_columns(df):
    return [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]


def clean_and_transform(df):
    df = df.with_columns(
        pl.col("timestamp")
        .cast(pl.String)
        .str.to_datetime(strict=False)
        .alias("timestamp")
    )

    numeric_columns = [
        "quantity",
        "price",
        "discount",
        "revenue",
        "session_duration",
        "pages_viewed",
    ]

    df = df.with_columns([
        pl.col(column)
        .cast(pl.Float64, strict=False)
        .alias(column)
        for column in numeric_columns
    ])

    df = df.filter(
        pl.col("timestamp").is_not_null()
        & (pl.col("quantity") > 0)
        & (pl.col("price") > 0)
        & (pl.col("revenue") > 0)
    )

    df = df.with_columns(
        pl.col("timestamp").dt.year().alias("year"),
        pl.col("timestamp").dt.month().alias("month"),
        pl.col("timestamp").dt.date().alias("transaction_date"),
        (pl.col("quantity") * pl.col("price")).alias("gross_amount"),
        (
            pl.col("quantity")
            * pl.col("price")
            * pl.col("discount")
            / 100
        ).alias("discount_amount"),
        (pl.col("revenue") / pl.col("quantity")).alias(
            "revenue_per_item"
        ),
    )

    return df


def process_uploaded_dataset(uploaded_file, admin_id):
    df = read_uploaded_file(uploaded_file)

    missing_columns = validate_columns(df)

    if missing_columns:
        return {
            "success": False,
            "error": "Missing required columns: "
            + ", ".join(missing_columns),
        }

    original_rows = df.height
    df = clean_and_transform(df)

    if df.height == 0:
        return {
            "success": False,
            "error": "No valid rows remain after cleaning.",
        }

    admin_directory = UPLOAD_ROOT / str(admin_id)
    admin_directory.mkdir(parents=True, exist_ok=True)

    output_path = admin_directory / "transactions_processed.parquet"
    df.write_parquet(output_path)

    return {
        "success": True,
        "output_path": str(output_path),
        "original_rows": original_rows,
        "processed_rows": df.height,
        "customers": df["customer_id"].n_unique(),
        "products": df["product_id"].n_unique(),
        "categories": df["category"].n_unique(),
        "cities": df["city"].n_unique(),
        "date_min": df["timestamp"].min(),
        "date_max": df["timestamp"].max(),
    }


def load_admin_data(admin_id):
    path = UPLOAD_ROOT / str(admin_id) / "transactions_processed.parquet"

    if not path.exists():
        return None

    return pd.read_parquet(path)


def show_admin_analytics(df):
    st.divider()
    st.header("Business Analytics")
    st.caption("Analytics generated from your uploaded dataset.")

    completed = df[
        df["order_status"].astype(str).str.lower().eq("completed")
    ].copy()

    if completed.empty:
        st.warning(
            "No completed orders were found. Upload data with "
            "order_status set to 'completed' to view sales KPIs."
        )
        return

    total_revenue = completed["revenue"].sum()
    total_transactions = completed["transaction_id"].nunique()
    customer_count = completed["customer_id"].nunique()

    average_order_value = (
        total_revenue / total_transactions
        if total_transactions
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Completed Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("Completed Transactions", f"{total_transactions:,}")
    col3.metric("Unique Customers", f"{customer_count:,}")
    col4.metric("Average Order Value", f"₹{average_order_value:,.2f}")

    st.subheader("Revenue by Category")

    category_data = (
        completed.groupby("category", as_index=False)
        .agg(revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
    )

    fig_category = px.bar(
        category_data,
        x="category",
        y="revenue",
        title="Revenue by Category",
        labels={"category": "Category", "revenue": "Revenue"},
    )
    fig_category.update_layout(height=400)
    st.plotly_chart(fig_category, width="stretch")

    left, right = st.columns(2)

    with left:
        city_data = (
            completed.groupby("city", as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values("revenue", ascending=False)
        )

        fig_city = px.bar(
            city_data,
            x="city",
            y="revenue",
            title="Revenue by City",
            labels={"city": "City", "revenue": "Revenue"},
        )
        fig_city.update_layout(height=400)
        st.plotly_chart(fig_city, width="stretch")

    with right:
        monthly_data = (
            completed.groupby(["year", "month"], as_index=False)
            .agg(revenue=("revenue", "sum"))
            .sort_values(["year", "month"])
        )

        monthly_data["month_date"] = pd.to_datetime(
            monthly_data["year"].astype(str)
            + "-"
            + monthly_data["month"].astype(str)
            + "-01"
        )

        fig_monthly = px.line(
            monthly_data,
            x="month_date",
            y="revenue",
            markers=True,
            title="Monthly Revenue Trend",
            labels={"month_date": "Month", "revenue": "Revenue"},
        )
        fig_monthly.update_layout(height=400)
        st.plotly_chart(fig_monthly, width="stretch")

    st.subheader("Uploaded Data Preview")
    st.dataframe(
        completed.head(100),
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Sales KPIs use completed orders only. "
        "The table displays up to 100 completed-order records."
    )


def show_admin_segmentation(df):
    st.divider()
    st.header("Customer Intelligence")
    st.caption(
        "K-Means segmentation calculated from your uploaded dataset."
    )

    try:
        result = segment_uploaded_customers(df)
    except Exception as error:
        st.error(f"Customer segmentation failed: {error}")
        return

    if not result["success"]:
        st.warning(result["error"])
        return

    customers = result["customers"]

    st.success(
        f"Segmentation completed for {len(customers):,} customers "
        f"across {result['clusters']} clusters."
    )

    segments = sorted(customers["customer_segment"].unique())

    selected_segments = st.multiselect(
        "Filter customer segments",
        options=segments,
        default=segments,
        key=f"admin_segment_filter_{st.session_state['user']['id']}",
    )

    filtered = customers[
        customers["customer_segment"].isin(selected_segments)
    ].copy()

    if filtered.empty:
        st.info("Select at least one segment to view its analytics.")
        return

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customers Segmented",
        f"{filtered['customer_id'].nunique():,}",
    )
    col2.metric(
        "Average Customer Spend",
        f"₹{filtered['total_spend'].mean():,.2f}",
    )
    col3.metric(
        "Average Transactions",
        f"{filtered['total_transactions'].mean():.2f}",
    )

    segment_counts = (
        filtered.groupby("customer_segment", as_index=False)
        .agg(customers=("customer_id", "nunique"))
        .sort_values("customers", ascending=False)
    )

    fig_distribution = px.bar(
        segment_counts,
        x="customer_segment",
        y="customers",
        text="customers",
        title="Customer Distribution by Segment",
        labels={
            "customer_segment": "Customer Segment",
            "customers": "Customers",
        },
    )
    fig_distribution.update_layout(height=420)
    st.plotly_chart(fig_distribution, width="stretch")

    segment_spend = (
        filtered.groupby("customer_segment", as_index=False)
        .agg(total_spend=("total_spend", "sum"))
        .sort_values("total_spend", ascending=False)
    )

    fig_spend = px.bar(
        segment_spend,
        x="customer_segment",
        y="total_spend",
        title="Total Spend by Customer Segment",
        labels={
            "customer_segment": "Customer Segment",
            "total_spend": "Total Spend (₹)",
        },
    )
    fig_spend.update_layout(height=420)
    st.plotly_chart(fig_spend, width="stretch")

    fig_activity = px.scatter(
        filtered,
        x="total_transactions",
        y="total_spend",
        color="customer_segment",
        hover_data=[
            "customer_id",
            "avg_order_value",
            "days_since_last_purchase",
        ],
        title="Customer Spend vs. Transaction Activity",
        labels={
            "total_transactions": "Transactions",
            "total_spend": "Total Spend (₹)",
            "customer_segment": "Customer Segment",
        },
    )
    fig_activity.update_layout(height=480)
    st.plotly_chart(fig_activity, width="stretch")

    st.subheader("Customer Segment Details")

    display_columns = [
        "customer_id",
        "total_spend",
        "total_transactions",
        "avg_order_value",
        "days_since_last_purchase",
        "cluster",
        "customer_segment",
    ]

    display_data = filtered[display_columns].copy().rename(
        columns={
            "customer_id": "Customer ID",
            "total_spend": "Total Spend",
            "total_transactions": "Transactions",
            "avg_order_value": "Average Order Value",
            "days_since_last_purchase": "Days Since Last Purchase",
            "cluster": "Cluster ID",
            "customer_segment": "Customer Segment",
        }
    )

    st.dataframe(
        display_data,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Segments are inferred from behavioral features in the uploaded "
        "dataset. Small datasets can produce unstable clusters."
    )


def show_admin_workspace(user):
    st.title("🛠️ Admin Workspace")
    st.caption(
        "Upload transaction data to generate business analytics "
        "and customer intelligence."
    )

    uploaded_file = st.file_uploader(
        "Upload a CSV or Parquet transaction dataset",
        type=["csv", "parquet"],
    )

    with st.expander("Required dataset columns"):
        st.code(", ".join(REQUIRED_COLUMNS))

    if uploaded_file is not None:
        st.write(f"Selected file: **{uploaded_file.name}**")

        if st.button("Process Dataset", type="primary"):
            try:
                with st.spinner("Validating and processing your dataset..."):
                    result = process_uploaded_dataset(
                        uploaded_file,
                        user["id"],
                    )
            except Exception as error:
                st.error(f"Processing failed: {error}")
                return

            if not result["success"]:
                st.error(result["error"])
                return

            st.success("Dataset validated and processed successfully.")

            col1, col2, col3 = st.columns(3)
            col1.metric("Original Rows", f"{result['original_rows']:,}")
            col2.metric("Processed Rows", f"{result['processed_rows']:,}")
            col3.metric("Unique Customers", f"{result['customers']:,}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Products", f"{result['products']:,}")
            col2.metric("Categories", f"{result['categories']:,}")
            col3.metric("Cities", f"{result['cities']:,}")

            st.write(
                f"**Date Range:** {result['date_min']} — {result['date_max']}"
            )

            st.session_state["admin_dataset_ready"] = True
            st.session_state["admin_dataset_path"] = result["output_path"]

    try:
        admin_df = load_admin_data(user["id"])
    except Exception as error:
        st.error(f"Could not load your processed dataset: {error}")
        return

    if admin_df is None:
        st.info("Upload a dataset to begin. No demo dataset is loaded here.")
        st.markdown(
            "**Processing:** Upload → Validate → Clean → Transform → Analyze"
        )
        return

    st.success("Your processed dataset is available for analysis.")

    show_admin_analytics(admin_df)
    show_admin_segmentation(admin_df)
    show_admin_churn_risk(admin_df)



def show_admin_churn_risk(df):
    """Display inactivity risk and rule-based retention recommendations."""
    st.divider()
    st.header("Customer Inactivity Risk")
    st.caption(
        "Rule-based inactivity analysis and retention recommendations "
        "from your uploaded transaction history. This is not a validated "
        "machine-learning churn prediction."
    )

    try:
        result = analyze_customer_inactivity(df)
    except Exception as error:
        st.error(f"Customer inactivity analysis failed: {error}")
        return

    if not result.get("success"):
        st.warning(result.get("error", "Could not analyze customer inactivity."))
        return

    customers = result["customers"].copy()
    reference_date = result["reference_date"]

    st.info(
        f"Reference date: {reference_date.date()}. Inactivity is measured "
        "from the latest transaction date in this uploaded dataset."
    )

    risk_options = ["Low", "Medium", "High"]
    selected_risks = st.multiselect(
        "Filter by inactivity risk",
        options=risk_options,
        default=risk_options,
        key=f"admin_inactivity_risk_{st.session_state['user']['id']}",
    )

    filtered = customers[
        customers["inactivity_risk"].isin(selected_risks)
    ].copy()

    if filtered.empty:
        st.info("Select at least one risk category to view customers.")
        return

    high_count = int((filtered["inactivity_risk"] == "High").sum())
    medium_count = int((filtered["inactivity_risk"] == "Medium").sum())
    low_count = int((filtered["inactivity_risk"] == "Low").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Customers Analyzed", f"{len(filtered):,}")
    col2.metric("High Inactivity", f"{high_count:,}")
    col3.metric("Medium Inactivity", f"{medium_count:,}")
    col4.metric("Low Inactivity", f"{low_count:,}")

    risk_counts = (
        filtered.groupby("inactivity_risk", as_index=False)
        .agg(customers=("customer_id", "nunique"))
    )
    risk_counts["inactivity_risk"] = pd.Categorical(
        risk_counts["inactivity_risk"],
        categories=risk_options,
        ordered=True,
    )
    risk_counts = risk_counts.sort_values("inactivity_risk")

    fig_risk = px.bar(
        risk_counts,
        x="inactivity_risk",
        y="customers",
        text="customers",
        title="Customers by Inactivity Risk",
        labels={
            "inactivity_risk": "Inactivity Risk",
            "customers": "Customers",
        },
    )
    fig_risk.update_layout(height=400)
    st.plotly_chart(fig_risk, width="stretch")

    fig_recency = px.histogram(
        filtered,
        x="days_since_last_purchase",
        color="inactivity_risk",
        nbins=20,
        title="Days Since Last Purchase",
        labels={
            "days_since_last_purchase": "Days Since Last Purchase",
            "count": "Customers",
            "inactivity_risk": "Inactivity Risk",
        },
    )
    fig_recency.update_layout(height=400)
    st.plotly_chart(fig_recency, width="stretch")

    st.subheader("Customer Retention Recommendations")

    priority_order = [
        "High Priority",
        "Retention Priority",
        "Re-engagement",
        "Engagement",
        "Loyalty Opportunity",
        "Maintain Engagement",
    ]

    priority_counts = (
        filtered.groupby("retention_priority", as_index=False)
        .agg(customers=("customer_id", "nunique"))
    )
    priority_counts["retention_priority"] = pd.Categorical(
        priority_counts["retention_priority"],
        categories=priority_order,
        ordered=True,
    )
    priority_counts = priority_counts.sort_values("retention_priority")

    fig_priority = px.bar(
        priority_counts,
        x="retention_priority",
        y="customers",
        text="customers",
        title="Customers by Retention Priority",
        labels={
            "retention_priority": "Retention Priority",
            "customers": "Customers",
        },
    )
    fig_priority.update_layout(height=420, xaxis_tickangle=-25)
    st.plotly_chart(fig_priority, width="stretch")

    st.subheader("Customer Retention Action List")

    display_columns = [
        "customer_id",
        "total_transactions",
        "total_spend",
        "days_since_last_purchase",
        "inactivity_risk",
        "retention_priority",
        "recommended_action",
        "recommendation_reason",
    ]

    display_data = filtered[display_columns].rename(
        columns={
            "customer_id": "Customer ID",
            "total_transactions": "Transactions",
            "total_spend": "Total Spend",
            "days_since_last_purchase": "Days Since Last Purchase",
            "inactivity_risk": "Inactivity Risk",
            "retention_priority": "Retention Priority",
            "recommended_action": "Recommended Action",
            "recommendation_reason": "Recommendation Reason",
        }
    )

    st.dataframe(
        display_data,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Inactivity thresholds are illustrative: Low = 0-30 days, "
        "Medium = 31-60 days, High = more than 60 days. Spending priority "
        "uses the median spend in this dataset. Recommendations are "
        "heuristics; validate them against the business's purchase cycle "
        "before making customer-facing decisions."
    )
