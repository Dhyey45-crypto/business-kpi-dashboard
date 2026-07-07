"""
KPI Dashboard - Streamlit + Plotly + TextBlob
------------------------------------------------
Run with:
    streamlit run app.py

Features:
  - Revenue KPI
  - Profit KPI
  - Customer Growth KPI
  - Monthly Trends (Plotly line charts)
  - Interactive Filters (date range, region, category, product)
  - Sentiment Analysis on customer feedback using TextBlob
  - Multiple Plotly visualizations (bar, line, pie, treemap)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from pathlib import Path

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "sales_data.csv"


# --------------------------------------------------------------------------
# DATA LOADING
# --------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["year"] = df["order_date"].dt.year
    return df


@st.cache_data
def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Use TextBlob to score each piece of customer feedback."""
    df = df.copy()

    def sentiment_label(text: str):
        polarity = TextBlob(str(text)).sentiment.polarity
        if polarity > 0.1:
            return "Positive", polarity
        elif polarity < -0.1:
            return "Negative", polarity
        else:
            return "Neutral", polarity

    labels, scores = zip(*df["customer_feedback"].apply(sentiment_label))
    df["sentiment"] = labels
    df["sentiment_score"] = scores
    return df


if not DATA_PATH.exists():
    st.error(
        f"Data file not found at {DATA_PATH}. "
        f"Run `python generate_data.py` first, or make sure "
        f"data/sales_data.csv exists."
    )
    st.stop()

raw_df = load_data(DATA_PATH)
df = add_sentiment(raw_df)

# --------------------------------------------------------------------------
# SIDEBAR - INTERACTIVE FILTERS
# --------------------------------------------------------------------------
st.sidebar.title("🔎 Filters")

min_date, max_date = df["order_date"].min(), df["order_date"].max()
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = sorted(df["region"].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

products_available = sorted(df[df["category"].isin(selected_categories)]["product"].unique())
selected_products = st.sidebar.multiselect("Product", products_available, default=products_available)

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit, Plotly & TextBlob")

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

mask = (
    (df["order_date"] >= pd.to_datetime(start_date))
    & (df["order_date"] <= pd.to_datetime(end_date))
    & (df["region"].isin(selected_regions))
    & (df["category"].isin(selected_categories))
    & (df["product"].isin(selected_products))
)
fdf = df.loc[mask].copy()

if fdf.empty:
    st.warning("No data matches the selected filters. Please broaden your filter selection.")
    st.stop()

# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------
st.title("📊 Business KPI Dashboard")
st.caption(
    f"Showing data from **{start_date}** to **{end_date}** | "
    f"{len(fdf):,} orders across {fdf['customer_id'].nunique():,} customers"
)

# --------------------------------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------------------------------
total_revenue = fdf["revenue"].sum()
total_profit = fdf["profit"].sum()
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0
total_customers = fdf["customer_id"].nunique()
avg_order_value = fdf["revenue"].mean()

# Customer growth: new customers per month vs overall dataset first-purchase month
first_purchase = df.groupby("customer_id")["order_date"].min().dt.to_period("M").dt.to_timestamp()
first_purchase_in_range = first_purchase[first_purchase.index.isin(fdf["customer_id"].unique())]
new_customers_in_range = first_purchase_in_range[
    (first_purchase_in_range >= pd.to_datetime(start_date).to_period("M").to_timestamp())
    & (first_purchase_in_range <= pd.to_datetime(end_date).to_period("M").to_timestamp())
].count()

# Growth rate vs previous equal-length period (simple comparison)
period_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
prev_start = pd.to_datetime(start_date) - pd.Timedelta(days=period_days)
prev_end = pd.to_datetime(start_date) - pd.Timedelta(days=1)
prev_mask = (
    (df["order_date"] >= prev_start)
    & (df["order_date"] <= prev_end)
    & (df["region"].isin(selected_regions))
    & (df["category"].isin(selected_categories))
)
prev_df = df.loc[prev_mask]
prev_revenue = prev_df["revenue"].sum()
prev_profit = prev_df["profit"].sum()
prev_customers = prev_df["customer_id"].nunique()

def pct_change(curr, prev):
    if prev == 0:
        return None
    return (curr - prev) / prev * 100

rev_delta = pct_change(total_revenue, prev_revenue)
profit_delta = pct_change(total_profit, prev_profit)
cust_delta = pct_change(total_customers, prev_customers)

# --------------------------------------------------------------------------
# KPI CARDS
# --------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.0f}",
    f"{rev_delta:+.1f}% vs prev. period" if rev_delta is not None else None,
)
col2.metric(
    "📈 Total Profit",
    f"${total_profit:,.0f}",
    f"{profit_delta:+.1f}% vs prev. period" if profit_delta is not None else None,
)
col3.metric(
    "👥 Customer Growth",
    f"{total_customers:,} customers",
    f"{cust_delta:+.1f}% vs prev. period" if cust_delta is not None else None,
)
col4.metric(
    "🧾 Avg Order Value",
    f"${avg_order_value:,.2f}",
    f"Margin: {profit_margin:.1f}%",
)

st.markdown("---")

# --------------------------------------------------------------------------
# MONTHLY TRENDS
# --------------------------------------------------------------------------
st.subheader("📆 Monthly Trends")

monthly = (
    fdf.groupby("month")
    .agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        customers=("customer_id", "nunique"),
        orders=("order_id", "count"),
    )
    .reset_index()
    .sort_values("month")
)

trend_tab1, trend_tab2, trend_tab3 = st.tabs(["Revenue & Profit", "Customer Growth", "Orders"])

with trend_tab1:
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["revenue"],
        mode="lines+markers", name="Revenue",
        line=dict(color="#2E86DE", width=3),
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["profit"],
        mode="lines+markers", name="Profit",
        line=dict(color="#10AC84", width=3),
    ))
    fig_trend.update_layout(
        xaxis_title="Month", yaxis_title="Amount ($)",
        hovermode="x unified", legend=dict(orientation="h", y=1.1),
        margin=dict(t=30),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with trend_tab2:
    fig_cust = px.bar(
        monthly, x="month", y="customers",
        labels={"month": "Month", "customers": "Active Customers"},
        color_discrete_sequence=["#F39C12"],
    )
    fig_cust.update_layout(margin=dict(t=30))
    st.plotly_chart(fig_cust, use_container_width=True)

with trend_tab3:
    fig_orders = px.line(
        monthly, x="month", y="orders", markers=True,
        labels={"month": "Month", "orders": "Number of Orders"},
        color_discrete_sequence=["#8E44AD"],
    )
    fig_orders.update_layout(margin=dict(t=30))
    st.plotly_chart(fig_orders, use_container_width=True)

st.markdown("---")

# --------------------------------------------------------------------------
# REGION / CATEGORY BREAKDOWN
# --------------------------------------------------------------------------
st.subheader("🗺️ Revenue & Profit Breakdown")

bcol1, bcol2 = st.columns(2)

with bcol1:
    region_summary = fdf.groupby("region").agg(revenue=("revenue", "sum"), profit=("profit", "sum")).reset_index()
    fig_region = px.bar(
        region_summary.sort_values("revenue", ascending=True),
        x="revenue", y="region", orientation="h",
        text_auto=".2s",
        labels={"revenue": "Revenue ($)", "region": "Region"},
        color="revenue", color_continuous_scale="Blues",
        title="Revenue by Region",
    )
    fig_region.update_layout(margin=dict(t=40), coloraxis_showscale=False)
    st.plotly_chart(fig_region, use_container_width=True)

with bcol2:
    cat_summary = fdf.groupby("category").agg(revenue=("revenue", "sum")).reset_index()
    fig_cat = px.pie(
        cat_summary, names="category", values="revenue",
        title="Revenue Share by Category", hole=0.45,
    )
    fig_cat.update_traces(textinfo="percent+label")
    fig_cat.update_layout(margin=dict(t=40))
    st.plotly_chart(fig_cat, use_container_width=True)

# Treemap: Category > Product revenue
prod_summary = fdf.groupby(["category", "product"]).agg(revenue=("revenue", "sum")).reset_index()
fig_tree = px.treemap(
    prod_summary, path=["category", "product"], values="revenue",
    color="revenue", color_continuous_scale="Greens",
    title="Revenue Drill-down: Category → Product",
)
fig_tree.update_layout(margin=dict(t=40))
st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")

# --------------------------------------------------------------------------
# SENTIMENT ANALYSIS (TextBlob)
# --------------------------------------------------------------------------
st.subheader("💬 Customer Feedback Sentiment (TextBlob)")

scol1, scol2 = st.columns([1, 1.4])

with scol1:
    sentiment_counts = fdf["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]
    color_map = {"Positive": "#10AC84", "Neutral": "#F39C12", "Negative": "#EE5253"}
    fig_sent = px.pie(
        sentiment_counts, names="sentiment", values="count",
        color="sentiment", color_discrete_map=color_map,
        title="Overall Sentiment Distribution", hole=0.4,
    )
    fig_sent.update_layout(margin=dict(t=40))
    st.plotly_chart(fig_sent, use_container_width=True)

with scol2:
    sentiment_by_month = (
        fdf.groupby(["month", "sentiment"]).size().reset_index(name="count")
    )
    fig_sent_trend = px.bar(
        sentiment_by_month, x="month", y="count", color="sentiment",
        color_discrete_map=color_map, barmode="stack",
        labels={"month": "Month", "count": "Feedback Count"},
        title="Sentiment Trend Over Time",
    )
    fig_sent_trend.update_layout(margin=dict(t=40), legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_sent_trend, use_container_width=True)

with st.expander("🔍 View sample feedback with sentiment scores"):
    st.dataframe(
        fdf[["order_date", "customer_id", "customer_feedback", "sentiment", "sentiment_score"]]
        .sort_values("order_date", ascending=False)
        .head(50)
        .reset_index(drop=True),
        use_container_width=True,
    )

st.markdown("---")

# --------------------------------------------------------------------------
# RAW DATA TABLE
# --------------------------------------------------------------------------
with st.expander("📄 View filtered raw data"):
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="filtered_kpi_data.csv",
        mime="text/csv",
    )

st.caption("Dashboard built with Streamlit • Plotly • TextBlob")
