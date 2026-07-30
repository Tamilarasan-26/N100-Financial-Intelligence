import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px
from dashboard.utils.db import (
    get_companies,
    get_home_kpis,
    get_sector_distribution,
    get_top_companies
)

st.title("🏠 Home Dashboard")

# ----------------------------
# Year Selector
# ----------------------------
selected_year = st.selectbox(
    "Select Financial Year",
    [2024, 2023, 2022, 2021, 2020, 2019],
    index=0
)

st.success(f"Selected Year : {selected_year}")

# Temporary check
companies = get_companies()

# ----------------------------
# Home KPIs
# ----------------------------

kpi = get_home_kpis(selected_year).iloc[0]

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric(
    "Total Companies",
    len(companies)
)

col2.metric(
    "Average ROE",
    f"{kpi['avg_roe']:.2f}%"
)

col3.metric(
    "Average P/E",
    f"{kpi['avg_pe']:.2f}"
)

col4.metric(
    "Average D/E",
    f"{kpi['avg_de']:.2f}"
)

col5.metric(
    "Revenue CAGR (5Y)",
    f"{kpi['avg_revenue_cagr']:.2f}%"
)

col6.metric(
    "Debt-Free Companies",
    int(kpi["debt_free_companies"])
)

# ----------------------------
# Sector Distribution
# ----------------------------

st.divider()

st.subheader("🏢 Sector Distribution")

sector_df = get_sector_distribution()

fig = px.pie(
    sector_df,
    names="broad_sector",
    values="company_count",
    hole=0.5,
    title="Companies by Sector"
)

fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

st.subheader("🏆 Top 5 Companies by Composite Score")

top5 = get_top_companies(selected_year)

st.dataframe(
    top5,
    use_container_width=True,
    hide_index=True
)