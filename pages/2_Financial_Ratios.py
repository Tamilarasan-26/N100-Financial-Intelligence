from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# Database Configuration
# =====================================================

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "nifty100.db"


# =====================================================
# Streamlit Configuration
# =====================================================

st.set_page_config(
    page_title="Financial Ratios",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Ratios Dashboard")


# =====================================================
# Load Companies
# =====================================================

@st.cache_data
def load_companies():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        id,
        company_name,
        broad_sector,
        market_cap_category
    FROM companies
    ORDER BY company_name
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =====================================================
# Load Financial Ratios
# =====================================================

@st.cache_data
def load_financial_ratios(company_id):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(company_id,)
    )

    conn.close()

    return df


# =====================================================
# Load Companies
# =====================================================

companies = load_companies()

if companies.empty:

    st.error("No companies found.")

    st.stop()


# =====================================================
# Sidebar
# =====================================================

st.sidebar.header("📌 Filters")

selected_company = st.sidebar.selectbox(
    "Select Company",
    companies["company_name"]
)


company = companies[
    companies["company_name"] == selected_company
].iloc[0]

company_id = company["id"]


# =====================================================
# Load Ratio Data
# =====================================================

ratios = load_financial_ratios(company_id)

annual_ratios = ratios[
    ratios["period_type"] == "ANNUAL"
].copy()

annual_ratios = annual_ratios.sort_values("year")


if annual_ratios.empty:

    st.warning("No Annual Financial Ratios Available.")

    st.stop()


# =====================================================
# Company Header
# =====================================================

st.header(company["company_name"])

st.caption(
    f"{company['broad_sector']} • {company['market_cap_category']}"
)


# =====================================================
# Company Information
# =====================================================

st.divider()

st.subheader("🏢 Company Information")

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Company ID",
        company_id
    )

with c2:

    st.metric(
        "Sector",
        company["broad_sector"]
    )

with c3:

    st.metric(
        "Market Cap",
        company["market_cap_category"]
    )


# =====================================================
# Latest Ratio Record
# =====================================================

latest = annual_ratios.iloc[-1]

latest_year = int(latest["year"])

# =====================================================
# Latest Financial KPIs
# =====================================================

latest = annual_ratios.iloc[-1]

latest_year = int(latest["year"])

st.divider()

title_col, year_col = st.columns([5, 1])

with title_col:
    st.subheader("📈 Latest Financial KPIs")

with year_col:
    st.metric(
        "Financial Year",
        f"FY {latest_year}"
    )


row1 = st.columns(4)

with row1[0]:
    st.metric(
        "ROE",
        (
            f"{latest['return_on_equity_pct']:.2f}%"
            if pd.notna(latest["return_on_equity_pct"])
            else "N/A"
        )
    )

with row1[1]:
    st.metric(
        "ROCE",
        (
            f"{latest['return_on_capital_employed_pct']:.2f}%"
            if pd.notna(latest["return_on_capital_employed_pct"])
            else "N/A"
        )
    )

with row1[2]:
    st.metric(
        "ROA",
        (
            f"{latest['return_on_assets_pct']:.2f}%"
            if pd.notna(latest["return_on_assets_pct"])
            else "N/A"
        )
    )

with row1[3]:
    st.metric(
        "Debt / Equity",
        (
            f"{latest['debt_to_equity']:.2f}"
            if pd.notna(latest["debt_to_equity"])
            else "N/A"
        )
    )


row2 = st.columns(4)

with row2[0]:
    st.metric(
        "Interest Coverage",
        (
            f"{latest['interest_coverage']:.2f}x"
            if pd.notna(latest["interest_coverage"])
            else "N/A"
        )
    )

with row2[1]:
    st.metric(
        "Net Profit Margin",
        (
            f"{latest['net_profit_margin_pct']:.2f}%"
            if pd.notna(latest["net_profit_margin_pct"])
            else "N/A"
        )
    )

with row2[2]:
    st.metric(
        "Operating Margin",
        (
            f"{latest['operating_profit_margin_pct']:.2f}%"
            if pd.notna(latest["operating_profit_margin_pct"])
            else "N/A"
        )
    )

with row2[3]:
    st.metric(
        "Asset Turnover",
        (
            f"{latest['asset_turnover']:.2f}"
            if pd.notna(latest["asset_turnover"])
            else "N/A"
        )
    )
    
    # =====================================================
# Financial Ratio Trends
# =====================================================

st.divider()

st.subheader("📈 Financial Ratio Trends")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "ROE",
        "ROCE",
        "ROA",
        "Debt / Equity",
        "Interest Coverage"
    ]
)


# =====================================================
# ROE Trend
# =====================================================

with tab1:

    fig = px.line(
        annual_ratios,
        x="year",
        y="return_on_equity_pct",
        markers=True,
        title="Return on Equity (ROE)"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="ROE (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# ROCE Trend
# =====================================================

with tab2:

    fig = px.line(
        annual_ratios,
        x="year",
        y="return_on_capital_employed_pct",
        markers=True,
        title="Return on Capital Employed (ROCE)"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="ROCE (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# ROA Trend
# =====================================================

with tab3:

    fig = px.line(
        annual_ratios,
        x="year",
        y="return_on_assets_pct",
        markers=True,
        title="Return on Assets (ROA)"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="ROA (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# Debt to Equity Trend
# =====================================================

with tab4:

    fig = px.line(
        annual_ratios,
        x="year",
        y="debt_to_equity",
        markers=True,
        title="Debt to Equity Ratio"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="Debt / Equity"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# Interest Coverage Trend
# =====================================================

with tab5:

    fig = px.line(
        annual_ratios,
        x="year",
        y="interest_coverage",
        markers=True,
        title="Interest Coverage Ratio"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="Interest Coverage (x)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
    # =====================================================
# Margin Analysis
# =====================================================

st.divider()

st.subheader("📊 Margin Analysis")

tab1, tab2 = st.tabs(
    [
        "Net Profit Margin",
        "Operating Profit Margin"
    ]
)

with tab1:

    fig = px.line(
        annual_ratios,
        x="year",
        y="net_profit_margin_pct",
        markers=True,
        title="Net Profit Margin (%)"
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="Net Profit Margin (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with tab2:

    fig = px.line(
        annual_ratios,
        x="year",
        y="operating_profit_margin_pct",
        markers=True,
        title="Operating Profit Margin (%)"
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        xaxis_title="Financial Year",
        yaxis_title="Operating Profit Margin (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# CAGR Analysis
# =====================================================

st.divider()

st.subheader("📈 Growth (CAGR) Analysis")

latest = annual_ratios.iloc[-1]

g1, g2, g3 = st.columns(3)

with g1:

    st.metric(
        "Revenue CAGR (5Y)",
        (
            f"{latest['revenue_cagr_5y_pct']:.2f}%"
            if pd.notna(latest["revenue_cagr_5y_pct"])
            else "N/A"
        )
    )

with g2:

    st.metric(
        "PAT CAGR (5Y)",
        (
            f"{latest['pat_cagr_5y_pct']:.2f}%"
            if pd.notna(latest["pat_cagr_5y_pct"])
            else "N/A"
        )
    )

with g3:

    st.metric(
        "EPS CAGR (5Y)",
        (
            f"{latest['eps_cagr_5y_pct']:.2f}%"
            if pd.notna(latest["eps_cagr_5y_pct"])
            else "N/A"
        )
    )


# =====================================================
# Cash Flow Quality
# =====================================================

st.divider()

st.subheader("💰 Cash Flow Quality")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Free Cash Flow",
        (
            f"₹{latest['free_cash_flow_cr']:,.0f} Cr"
            if pd.notna(latest["free_cash_flow_cr"])
            else "N/A"
        )
    )

with c2:

    st.metric(
        "CFO Quality",
        (
            f"{latest['cfo_quality_score']:.2f}"
            if pd.notna(latest["cfo_quality_score"])
            else "N/A"
        )
    )

with c3:

    st.metric(
        "FCF Conversion",
        (
            f"{latest['fcf_conversion_rate_pct']:.2f}%"
            if pd.notna(latest["fcf_conversion_rate_pct"])
            else "N/A"
        )
    )

with c4:

    st.metric(
        "Capex Intensity",
        (
            f"{latest['capex_intensity_pct']:.2f}%"
            if pd.notna(latest["capex_intensity_pct"])
            else "N/A"
        )
    )


# =====================================================
# Financial Ratios Table
# =====================================================

st.divider()

st.subheader("📋 Annual Financial Ratios")

display_df = annual_ratios.sort_values(
    "year",
    ascending=False
).round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =====================================================
# Download CSV
# =====================================================

st.download_button(
    label="📥 Download Financial Ratios CSV",
    data=display_df.to_csv(index=False),
    file_name=f"{company_id}_financial_ratios.csv",
    mime="text/csv"
)


# =====================================================
# Financial Health Insights
# =====================================================

st.divider()

st.subheader("💡 Financial Health Insights")

if pd.notna(latest["return_on_equity_pct"]):

    if latest["return_on_equity_pct"] >= 20:
        st.success("✅ Strong Return on Equity.")

    elif latest["return_on_equity_pct"] >= 15:
        st.info("🟢 Healthy Return on Equity.")

    else:
        st.warning("🟠 Low Return on Equity.")


if pd.notna(latest["debt_to_equity"]):

    if latest["debt_to_equity"] < 0.5:
        st.success("✅ Low financial leverage.")

    elif latest["debt_to_equity"] < 1:
        st.info("🟢 Moderate leverage.")

    else:
        st.warning("🔴 High Debt-to-Equity ratio.")


if pd.notna(latest["interest_coverage"]):

    if latest["interest_coverage"] > 5:
        st.success("✅ Excellent interest coverage.")

    elif latest["interest_coverage"] > 2:
        st.info("🟢 Adequate interest coverage.")

    else:
        st.warning("🔴 Weak interest coverage.")


if pd.notna(latest["cfo_quality_score"]):

    if latest["cfo_quality_score"] >= 1:
        st.success("✅ Strong cash flow quality.")

    else:
        st.warning("🟠 Cash flow quality needs attention.")