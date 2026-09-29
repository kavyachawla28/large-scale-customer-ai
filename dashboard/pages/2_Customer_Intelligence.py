import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Customer Intelligence",
    page_icon="👥",
    layout="wide",
)


@st.cache_data
def load_customer_segments():
    path = "data/processed/powerbi_customer_segments.parquet"
    return pd.read_parquet(path)


customers = load_customer_segments()


st.title("👥 Customer Intelligence")
st.caption("Customer segmentation and behavioral analysis")

st.markdown(
    """
    Explore customer behavior using the segments generated
    by the machine-learning clustering pipeline.
    """
)


# Sidebar filters
st.sidebar.header("Customer Filters")

segments = sorted(customers["customer_segment"].unique())

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments,
)

filtered = customers[
    customers["customer_segment"].isin(selected_segments)
].copy()


# KPIs
customer_count = filtered["customer_id"].nunique()
total_spend = filtered["total_spend"].sum()
total_transactions = filtered["total_transactions"].sum()
avg_recency = filtered["days_since_last_purchase"].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Customers", f"{customer_count:,}")

with col2:
    st.metric("Total Customer Spend", f"₹{total_spend / 1e9:.2f}B")

with col3:
    st.metric("Transactions", f"{total_transactions:,.0f}")

with col4:
    st.metric("Avg. Recency", f"{avg_recency:.0f} days")


st.divider()


# Customer distribution
segment_counts = (
    filtered
    .groupby("customer_segment", as_index=False)
    .agg(customers=("customer_id", "nunique"))
    .sort_values("customers", ascending=False)
)

fig_segments = px.bar(
    segment_counts,
    x="customer_segment",
    y="customers",
    title="Customer Distribution by Segment",
    labels={
        "customer_segment": "Customer Segment",
        "customers": "Customers",
    },
    text="customers",
)

fig_segments.update_layout(height=420)

fig_segments.update_traces(
    texttemplate="%{text:,}",
    textposition="outside",
)

st.plotly_chart(
    fig_segments,
    use_container_width=True,
)


# Segment behavior
segment_behavior = (
    filtered
    .groupby("customer_segment", as_index=False)
    .agg(
        total_spend=("total_spend", "sum"),
        transactions=("total_transactions", "sum"),
        avg_order_value=("avg_order_value", "mean"),
        avg_recency=("days_since_last_purchase", "mean"),
    )
)


col1, col2 = st.columns(2)

with col1:

    fig_spend = px.bar(
        segment_behavior,
        x="customer_segment",
        y="total_spend",
        title="Total Spend by Customer Segment",
        labels={
            "customer_segment": "Customer Segment",
            "total_spend": "Total Spend",
        },
    )

    fig_spend.update_layout(
        height=420,
        yaxis_tickformat=".2s",
    )

    st.plotly_chart(
        fig_spend,
        use_container_width=True,
    )


with col2:

    fig_transactions = px.bar(
        segment_behavior,
        x="customer_segment",
        y="transactions",
        title="Transactions by Customer Segment",
        labels={
            "customer_segment": "Customer Segment",
            "transactions": "Transactions",
        },
    )

    fig_transactions.update_layout(height=420)

    st.plotly_chart(
        fig_transactions,
        use_container_width=True,
    )


# Customer value vs engagement
st.subheader("Customer Value vs. Engagement")

fig_scatter = px.scatter(
    filtered,
    x="total_transactions",
    y="total_spend",
    color="customer_segment",
    size="avg_order_value",
    hover_data=[
        "customer_id",
        "days_since_last_purchase",
        "active_months",
        "category_count",
    ],
    title="Customer Spend vs. Transaction Activity",
    labels={
        "total_transactions": "Total Transactions",
        "total_spend": "Total Spend",
        "customer_segment": "Customer Segment",
    },
    opacity=0.65,
)

fig_scatter.update_layout(height=550)

st.plotly_chart(
    fig_scatter,
    use_container_width=True,
)


# Segment profile
st.subheader("Segment Behavioral Profile")

profile = (
    filtered
    .groupby("customer_segment", as_index=False)
    .agg(
        Customers=("customer_id", "nunique"),
        Avg_Spend=("total_spend", "mean"),
        Avg_Transactions=("total_transactions", "mean"),
        Avg_Order_Value=("avg_order_value", "mean"),
        Avg_Recency_Days=("days_since_last_purchase", "mean"),
        Avg_Active_Months=("active_months", "mean"),
    )
)

st.dataframe(
    profile,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    f"Showing {len(filtered):,} customers across the selected segments."
)