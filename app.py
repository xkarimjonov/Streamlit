from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM STYLE
# =========================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-top: 0.2rem;
            margin-bottom: 1.5rem;
        }

        div[data-testid="stMetric"] {
            background-color: #f8fafc;
            border: 1px solid #e5e7eb;
            padding: 18px;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = Path(__file__).parent / "data" / "sales.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df["Date"] = pd.to_datetime(df["Date"])

    return df


df = load_data()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<p class="main-title">📊 Sales Analytics Dashboard</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="subtitle">'
    "Savdo ma'lumotlarini interaktiv tahlil qilish va vizuallashtirish"
    "</p>",
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎛 Dashboard Filters")

st.sidebar.markdown("Ma'lumotlarni filtrlash:")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Sana oralig'i",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = st.sidebar.multiselect(
    "🌍 Hudud",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)

categories = st.sidebar.multiselect(
    "📦 Kategoriya",
    options=sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique()),
)

products = st.sidebar.multiselect(
    "🛍 Mahsulot",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique()),
)


# =========================================================
# FILTER DATA
# =========================================================

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
        & (df["Region"].isin(regions))
        & (df["Category"].isin(categories))
        & (df["Product"].isin(products))
    ]
else:
    filtered_df = df[
        (df["Region"].isin(regions))
        & (df["Category"].isin(categories))
        & (df["Product"].isin(products))
    ]


# =========================================================
# EMPTY DATA CHECK
# =========================================================

if filtered_df.empty:
    st.warning(
        "⚠️ Tanlangan filterlar bo'yicha ma'lumot topilmadi. "
        "Filterlarni o'zgartirib ko'ring."
    )
    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = len(filtered_df)

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales > 0
    else 0
)


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📌 Asosiy ko'rsatkichlar")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Umumiy sotuv",
    f"{total_sales:,.0f} so'm",
)

col2.metric(
    "📈 Umumiy foyda",
    f"{total_profit:,.0f} so'm",
)

col3.metric(
    "📦 Sotilgan miqdor",
    f"{total_quantity:,}",
)

col4.metric(
    "🧾 Buyurtmalar",
    f"{total_orders:,}",
)

col5.metric(
    "📊 Foyda marjasi",
    f"{profit_margin:.1f}%",
)


st.divider()


# =========================================================
# SALES TREND
# =========================================================

st.subheader("📈 Sotuvlar dinamikasi")

sales_by_date = (
    filtered_df
    .assign(Date=filtered_df["Date"].dt.date)
    .groupby("Date", as_index=False)["Sales"]
    .sum()
)

fig_sales = px.line(
    sales_by_date,
    x="Date",
    y="Sales",
    markers=True,
    labels={
        "Date": "Sana",
        "Sales": "Sotuv",
    },
)

fig_sales.update_layout(
    hovermode="x unified",
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(
    fig_sales,
    use_container_width=True,
)


# =========================================================
# PRODUCT + REGION
# =========================================================

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# TOP PRODUCTS
# ---------------------------------------------------------

with col1:

    st.subheader("🏆 Mahsulotlar bo'yicha sotuv")

    product_sales = (
        filtered_df
        .groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_product = px.bar(
        product_sales,
        x="Sales",
        y="Product",
        orientation="h",
        labels={
            "Sales": "Sotuv",
            "Product": "Mahsulot",
        },
    )

    fig_product.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis={"categoryorder": "total ascending"},
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True,
    )


# ---------------------------------------------------------
# REGION ANALYSIS
# ---------------------------------------------------------

with col2:

    st.subheader("🌍 Hududlar bo'yicha sotuv")

    region_sales = (
        filtered_df
        .groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        labels={
            "Region": "Hudud",
            "Sales": "Sotuv",
        },
    )

    fig_region.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
    )


# =========================================================
# CATEGORY ANALYSIS
# =========================================================

st.subheader("📦 Kategoriyalar bo'yicha tahlil")

category_sales = (
    filtered_df
    .groupby("Category", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
    )
)

fig_category = px.bar(
    category_sales,
    x="Category",
    y=["Sales", "Profit"],
    barmode="group",
    labels={
        "Category": "Kategoriya",
        "value": "Summa",
        "variable": "Ko'rsatkich",
    },
)

fig_category.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(
    fig_category,
    use_container_width=True,
)


# =========================================================
# DATA TABLE
# =========================================================

st.subheader("📋 Sotuv ma'lumotlari")

st.caption(
    f"Ko'rsatilayotgan yozuvlar: {len(filtered_df):,} ta"
)

display_df = filtered_df.copy()

display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

display_df = display_df.sort_values(
    "Date",
    ascending=False,
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# DOWNLOAD BUTTON
# =========================================================

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Filtrlangan CSV yuklab olish",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📊 Sales Analytics Dashboard • "
    "Built with Python, Pandas, Plotly & Streamlit"
)