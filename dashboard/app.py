
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px


# ---------------------------------------------------------
# Make project root available for imports
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Project imports
# ---------------------------------------------------------
from auth.database import initialize_database, get_user_by_id
from dashboard.auth_page import show_auth_page
from dashboard.admin_workspace import show_admin_workspace


# ---------------------------------------------------------
# Initialize authentication database
# ---------------------------------------------------------
initialize_database()


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer AI Analytics",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None


# ---------------------------------------------------------
# Session cleanup
# ---------------------------------------------------------
def clear_user_session():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

    for key in list(st.session_state.keys()):
        if key.startswith("admin_"):
            st.session_state.pop(key, None)


# ---------------------------------------------------------
# Authentication gate
# ---------------------------------------------------------
if not st.session_state["authenticated"] or not st.session_state["user"]:
    clear_user_session()
    show_auth_page()
    st.stop()


# ---------------------------------------------------------
# Revalidate logged-in user against database
# ---------------------------------------------------------
session_user = st.session_state["user"]

try:
    user_id = session_user.get("id")
    db_user = get_user_by_id(user_id) if user_id is not None else None

except Exception:
    clear_user_session()
    st.error("Unable to verify your account. Please log in again.")
    st.stop()


if db_user is None:
    clear_user_session()
    st.warning("Your account could not be verified. Please log in again.")
    st.stop()


db_user_id, db_name, db_email, _, db_role = db_user

if db_role not in ("admin", "customer"):
    clear_user_session()
    st.error("Invalid account role. Please contact the administrator.")
    st.stop()


# Use trusted database values, not session-supplied role values.
user = {
    "id": db_user_id,
    "name": db_name,
    "email": db_email,
    "role": db_role,
}

st.session_state["user"] = user

user_name = user["name"]
user_role = user["role"]


# ---------------------------------------------------------
# Sidebar user information
# ---------------------------------------------------------
st.sidebar.success(f"Logged in as {user_name}")
st.sidebar.write(f"**Role:** {user_role.title()}")

if st.sidebar.button("Logout"):
    clear_user_session()
    st.rerun()


# ---------------------------------------------------------
# ADMIN VIEW
# Admins upload and process their own datasets.
# ---------------------------------------------------------
if user_role == "admin":
    show_admin_workspace(user)
    st.stop()


# ---------------------------------------------------------
# CUSTOMER VIEW
# Customers can view the read-only synthetic demo dashboard.
# ---------------------------------------------------------
@st.cache_data
def load_sales_data():
    path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "powerbi_sales_summary.parquet"
    )

    if not path.exists():
        raise FileNotFoundError(
            "The customer demo dashboard dataset was not found. "
            "Expected file: data/processed/powerbi_sales_summary.parquet"
        )

    df = pd.read_parquet(path)

    required_columns = [
        "year",
        "month",
        "category",
        "city",
        "transactions",
        "revenue",
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "The customer demo dataset is missing columns: "
            + ", ".join(missing)
        )

    df["date"] = pd.to_datetime(
        df["year"].astype(str)
        + "-"
        + df["month"].astype(str)
        + "-01",
        errors="coerce",
    )

    return df


try:
    sales = load_sales_data()
except Exception as error:
    st.error(f"Could not load the customer demo dashboard: {error}")
    st.stop()


# ---------------------------------------------------------
# Customer header
# ---------------------------------------------------------
st.title("📊 Customer AI Analytics")

st.caption("Large-Scale Customer Analytics & AI Platform")

st.markdown(
    """
    Welcome to the customer analytics workspace.

    Explore business performance, customer behavior,
    and AI-driven customer risk insights.
    """
)

st.info(
    "Customer Demo View — the dashboard currently uses "
    "the project's synthetic dataset. It is read-only; "
    "customers cannot upload or modify datasets."
)


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Dashboard Filters")

years = sorted(sales["year"].dropna().unique().tolist())
categories = sorted(sales["category"].dropna().unique().tolist())
cities = sorted(sales["city"].dropna().unique().tolist())

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years,
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=categories,
)

selected_cities = st.sidebar.multiselect(
    "City",
    options=cities,
    default=cities,
)


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------
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

average_order_value = (
    total_revenue / total_transactions
    if total_transactions > 0
    else 0
)


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
# Show charts only when filters return data
# ---------------------------------------------------------
if filtered.empty:
    st.warning(
        "No records match the selected filters. "
        "Select at least one year, category, and city."
    )
    st.stop()


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

st.plotly_chart(fig_category, width="stretch")


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

st.plotly_chart(fig_city, width="stretch")


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

st.plotly_chart(fig_monthly, width="stretch")


# ---------------------------------------------------------
# Data coverage
# ---------------------------------------------------------
st.caption(
    f"Showing {len(filtered):,} analytical records "
    "across the selected filters."
)
