import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Sales Dashboard")
st.write("Savdo ma'lumotlari bo'yicha interaktiv dashboard")

# Load data
df = pd.read_csv("data/sales.csv")

# Convert date
df["Date"] = pd.to_datetime(df["Date"])

# Sidebar filters
st.sidebar.header("🔎 Filterlar")

regions = st.sidebar.multiselect(
    "Hududni tanlang:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

categories = st.sidebar.multiselect(
    "Kategoriyani tanlang:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories))
]

# KPI calculations
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = len(filtered_df)

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Umumiy sotuv",
    f"${total_sales:,.0f}"
)

col2.metric(
    "📈 Umumiy foyda",
    f"${total_profit:,.0f}"
)

col3.metric(
    "📦 Sotilgan mahsulot",
    f"{total_quantity:,}"
)

col4.metric(
    "🧾 Buyurtmalar",
    f"{total_orders:,}"
)

st.divider()

# Sales by date
sales_by_date = (
    filtered_df
    .groupby("Date", as_index=False)["Sales"]
    .sum()
)

fig_sales = px.line(
    sales_by_date,
    x="Date",
    y="Sales",
    title="📈 Vaqt bo'yicha sotuvlar",
    markers=True
)

st.plotly_chart(fig_sales, use_container_width=True)

# Two columns
col1, col2 = st.columns(2)

# Sales by product
with col1:

    product_sales = (
        filtered_df
        .groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_product = px.bar(
        product_sales,
        x="Product",
        y="Sales",
        title="🏆 Mahsulotlar bo'yicha sotuv"
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )

# Sales by region
with col2:

    region_sales = (
        filtered_df
        .groupby("Region", as_index=False)["Sales"]
        .sum()
    )

    fig_region = px.pie(
        region_sales,
        names="Region",
        values="Sales",
        title="🗺️ Hududlar bo'yicha sotuv"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

# Data table
st.subheader("📋 Sotuv ma'lumotlari")

st.dataframe(
    filtered_df,
    use_container_width=True
)