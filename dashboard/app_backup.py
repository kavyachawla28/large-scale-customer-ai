import streamlit as st
import pandas as pd
import plotly.express as px


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer AI Analytics",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Load analytical dataset
# ---------------------------------------------------------
@st.cache_data
def load_sales_data():
    path = "data/processed/powerbi_sales_summary.parquet"
    df = pd.read_parquet(path)

    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" +
        df["month"].astype(str) + "-01"
    )

    return df


sales = load_sales_data()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("📊 Customer AI Analytics")
st.caption(
    "Large-Scale Customer Analytics & AI Platform"
)

st.markdown(
    """
    Analyze business performance, customer behavior,
    and AI-driven customer risk from processed analytical data.
    """
)


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Dashboard Filters")

years = sorted(sales["year"].unique())
categories = sorted(sales["category"].unique())
cities = sorted(sales["city"].unique())

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years,
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories,
)

selected_cities = st.sidebar.multiselect(
    "City",
    cities,
    default=cities,
)


filtered = sales[
    sales["year"].isin(selected_years)
    & sales["category"].isin(selected_categories)
    & sales["city"].isin(selected_cities)
].copy()


# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------
total_revenue = filtered["revenue"].sum()
total_transactions = filtered["transactions"].sum()

if total_transactions > 0:
    average_order_value = total_revenue / total_transactions
else:
    average_order_value = 0


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Revenue",
        f"₹{total_revenue / 1e9:.2f}B",
    )

with col2:
    st.metric(
        "Total Transactions",
        f"{total_transactions / 1e3:.0f}K",
    )

with col3:
    st.metric(
        "Average Order Value",
        f"₹{average_order_value:,.0f}",
    )


st.divider()


# ---------------------------------------------------------
# Revenue by Category
# ---------------------------------------------------------
category_data = (
    filtered
    .groupby("category", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

fig_category = px.bar(
    category_data,
    x="category",
    y="revenue",
    title="Revenue by Category",
    labels={
        "category": "Category",
        "revenue": "Revenue",
    },
)

fig_category.update_layout(
    height=420,
    yaxis_tickformat=".2s",
)

st.plotly_chart(
    fig_category,
    use_container_width=True,
)


# ---------------------------------------------------------
# Revenue by City
# ---------------------------------------------------------
city_data = (
    filtered
    .groupby("city", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

fig_city = px.bar(
    city_data,
    x="city",
    y="revenue",
    title="Revenue by City",
    labels={
        "city": "City",
        "revenue": "Revenue",
    },
)

fig_city.update_layout(
    height=420,
    yaxis_tickformat=".2s",
)

st.plotly_chart(
    fig_city,
    use_container_width=True,
)


# ---------------------------------------------------------
# Monthly Revenue Trend
# ---------------------------------------------------------
monthly_data = (
    filtered
    .groupby("date", as_index=False)["revenue"]
    .sum()
    .sort_values("date")
)

fig_monthly = px.line(
    monthly_data,
    x="date",
    y="revenue",
    markers=True,
    title="Monthly Revenue Trend",
    labels={
        "date": "Month",
        "revenue": "Revenue",
    },
)

fig_monthly.update_layout(
    height=450,
    yaxis_tickformat=".2s",
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True,
)


# ---------------------------------------------------------
# Data coverage
# ---------------------------------------------------------
st.caption(
    f"Showing {len(filtered):,} analytical records "
    f"across the selected filters."
)