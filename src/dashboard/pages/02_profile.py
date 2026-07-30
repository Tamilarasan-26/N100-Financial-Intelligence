import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px

from dashboard.utils.db import (
    get_companies,
    get_company_info,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_valuation,
    get_company_insights
)

st.title("🏢 Company Profile")

# Company Dropdown
companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["id"]
)
info = get_company_info(company)

if info.empty:
    st.error("❌ Ticker not found. Please try another.")
    st.stop()

company_info = info.iloc[0]

st.markdown("## 🏢 Company Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Company:**", company_info["company_name"])
    st.write("**Sector:**", company_info["broad_sector"])
    st.write("**Sub Sector:**", company_info["sub_sector"])

with col2:
    st.write("**Website:**", company_info["website"])
    st.write("**About:**")
    st.write(company_info["about_company"])

# -----------------------------
# Financial Ratios
# -----------------------------
ratios = get_ratios(company)
latest = ratios.iloc[0]

st.subheader("📊 Key Financial Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "ROE",
        f"{latest['return_on_equity_pct']:.2f}%"
    )

with col2:
    st.metric(
        "ROCE",
        f"{latest['return_on_capital_employed_pct']:.2f}%"
    )

with col3:
    st.metric(
        "Net Profit Margin",
        f"{latest['net_profit_margin_pct']:.2f}%"
    )

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "Debt / Equity",
        f"{latest['debt_to_equity']:.2f}"
    )

with col5:
    st.metric(
        "Revenue CAGR (5Y)",
        f"{latest['revenue_cagr_5y_pct']:.2f}%"
    )

with col6:
    st.metric(
        "Free Cash Flow",
        f"{latest['free_cash_flow_cr']:.2f} Cr"
    )



# -----------------------------
# Profit & Loss
# -----------------------------
pl = get_pl(company)


# -----------------------------
# Revenue & Net Profit Trend
# -----------------------------

st.subheader("📈 Revenue & Net Profit Trend")

if not pl.empty:

    chart_df = pl.sort_values("year")

    fig = px.line(
        chart_df,
        x="year",
        y=["sales", "net_profit"],
        markers=True,
        title="Revenue vs Net Profit"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# -----------------------------
# ROE vs ROCE Trend
# -----------------------------

st.subheader("📊 ROE vs ROCE Trend")

if not ratios.empty:

    ratio_chart = ratios.sort_values("year")

    fig = px.line(
        ratio_chart,
        x="year",
        y=[
            "return_on_equity_pct",
            "return_on_capital_employed_pct"
        ],
        markers=True,
        title="ROE vs ROCE"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )
    
st.subheader("✅ Pros & ❌ Cons")

insights = get_company_insights(company)

if not insights.empty:

    row = insights.iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.success(row["pros"] if pd.notna(row["pros"]) else "No Pros Available")

    with col2:
        st.error(row["cons"] if pd.notna(row["cons"]) else "No Cons Available")

else:
    st.info("No insights available for this company.")