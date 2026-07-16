from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st
import plotly.express as px


# =====================================================
# Database Configuration
# =====================================================

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "nifty100.db"


# =====================================================
# Streamlit Configuration
# =====================================================

st.set_page_config(
    page_title="Company Overview",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Company Overview")


# =====================================================
# Database Functions
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


@st.cache_data
def load_profit_and_loss(company_id):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        year,
        period_type,
        sales,
        operating_profit,
        net_profit
    FROM profitandloss
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

    st.error("No companies found in database.")

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
# Load Company Data
# =====================================================

pnl = load_profit_and_loss(company_id)

annual = pnl[
    pnl["period_type"] == "ANNUAL"
].copy()


ratios = load_financial_ratios(company_id)

annual_ratios = ratios[
    ratios["period_type"] == "ANNUAL"
].copy()


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

info1, info2, info3 = st.columns(3)

with info1:

    st.metric(
        "Company ID",
        company["id"]
    )

with info2:

    st.metric(
        "Sector",
        company["broad_sector"]
    )

with info3:

    st.metric(
        "Market Cap",
        company["market_cap_category"]
    )


# =====================================================
# Company Summary
# =====================================================

st.divider()

st.subheader("📋 Company Summary")

left, right = st.columns(2)

with left:

    st.write("**Company Name**")
    st.write(company["company_name"])

    st.write("**Company ID**")
    st.write(company["id"])

    st.write("**Sector**")
    st.write(company["broad_sector"])

with right:

    st.write("**Market Cap Category**")
    st.write(company["market_cap_category"])

    latest_year = (
        int(annual["year"].max())
        if not annual.empty
        else "N/A"
    )

    st.write("**Latest Financial Year**")
    st.write(f"FY {latest_year}")

    st.write("**Annual Reports Available**")
    st.write(len(annual))

    st.write("**Financial Ratio Records**")
    st.write(len(annual_ratios))


# =====================================================
# Stop if no Annual Data
# =====================================================

if annual.empty:

    st.warning("No Annual Financial Data Available.")

    st.stop()
    
# =====================================================
# Latest Financial Data
# =====================================================

latest_pnl = annual.iloc[-1]

revenue = latest_pnl["sales"]
operating_profit = latest_pnl["operating_profit"]
net_profit = latest_pnl["net_profit"]

latest_year = int(latest_pnl["year"])

if annual_ratios.empty:

    roe = None
    roce = None
    roa = None
    debt = None
    icr = None

else:

    latest_ratio = annual_ratios.iloc[-1]

    roe = latest_ratio["return_on_equity_pct"]
    roce = latest_ratio["return_on_capital_employed_pct"]
    roa = latest_ratio["return_on_assets_pct"]
    debt = latest_ratio["debt_to_equity"]
    icr = latest_ratio["interest_coverage"]


# =====================================================
# KPI Dashboard
# =====================================================

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
        "Revenue",
        f"₹{revenue:,.0f} Cr"
    )

with row1[1]:

    st.metric(
        "Operating Profit",
        f"₹{operating_profit:,.0f} Cr"
    )

with row1[2]:

    st.metric(
        "Net Profit",
        f"₹{net_profit:,.0f} Cr"
    )

with row1[3]:

    st.metric(
        "ROE",
        (
            f"{roe:.2f}%"
            if pd.notna(roe)
            else "N/A"
        )
    )

row2 = st.columns(4)

with row2[0]:

    st.metric(
        "ROCE",
        (
            f"{roce:.2f}%"
            if pd.notna(roce)
            else "N/A"
        )
    )

with row2[1]:

    st.metric(
        "ROA",
        (
            f"{roa:.2f}%"
            if pd.notna(roa)
            else "N/A"
        )
    )

with row2[2]:

    st.metric(
        "Debt / Equity",
        (
            f"{debt:.2f}"
            if pd.notna(debt)
            else "N/A"
        )
    )

with row2[3]:

    st.metric(
        "Interest Coverage",
        (
            f"{icr:.2f}x"
            if pd.notna(icr)
            else "N/A"
        )
    )


# =====================================================
# Latest Financial Snapshot
# =====================================================

roe_text = (
    f"{roe:.2f}%"
    if pd.notna(roe)
    else "N/A"
)

debt_text = (
    f"{debt:.2f}"
    if pd.notna(debt)
    else "N/A"
)

icr_text = (
    f"{icr:.2f}x"
    if pd.notna(icr)
    else "N/A"
)

st.info(
f"""
### 📌 Latest Financial Snapshot

**Revenue:** ₹{revenue:,.0f} Cr

**Operating Profit:** ₹{operating_profit:,.0f} Cr

**Net Profit:** ₹{net_profit:,.0f} Cr

**ROE:** {roe_text}

**Debt / Equity:** {debt_text}

**Interest Coverage:** {icr_text}
"""
)


# =====================================================
# Financial Performance
# =====================================================

st.divider()

st.subheader("📈 Financial Performance")

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Revenue",
        "🏭 Operating Profit",
        "💰 Net Profit"
    ]
)


# =====================================================
# Revenue Trend
# =====================================================

with tab1:

    fig = px.line(
        annual,
        x="year",
        y="sales",
        markers=True,
        title="Revenue Trend"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=600,
        font=dict(size=15),
        title_x=0.02,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis_title="Financial Year",
        yaxis_title="Revenue (₹ Cr)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# Operating Profit Trend
# =====================================================

with tab2:

    fig = px.line(
        annual,
        x="year",
        y="operating_profit",
        markers=True,
        title="Operating Profit Trend"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=600,
        font=dict(size=15),
        title_x=0.02,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis_title="Financial Year",
        yaxis_title="Operating Profit (₹ Cr)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# Net Profit Trend
# =====================================================

with tab3:

    fig = px.line(
        annual,
        x="year",
        y="net_profit",
        markers=True,
        title="Net Profit Trend"
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=600,
        font=dict(size=15),
        title_x=0.02,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        xaxis_title="Financial Year",
        yaxis_title="Net Profit (₹ Cr)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# Revenue Growth
# =====================================================

st.divider()

st.subheader("📊 Revenue Growth")

annual["Revenue Growth %"] = (
    annual["sales"].pct_change() * 100
)

fig = px.bar(
    annual,
    x="year",
    y="Revenue Growth %",
    title="Year-over-Year Revenue Growth"
)

fig.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================================
# Profit Growth
# =====================================================

st.divider()

st.subheader("💰 Net Profit Growth")

annual["Profit Growth %"] = (
    annual["net_profit"].pct_change() * 100
)

fig = px.bar(
    annual,
    x="year",
    y="Profit Growth %",
    title="Year-over-Year Net Profit Growth"
)

fig.update_layout(
    template="plotly_white",
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# Annual Profit & Loss
# =====================================================

st.divider()

st.subheader("📑 Annual Profit & Loss")

display_pnl = annual.copy()

display_pnl = display_pnl.sort_values(
    "year",
    ascending=False
)

st.dataframe(
    display_pnl,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="📥 Download Profit & Loss CSV",
    data=display_pnl.to_csv(index=False),
    file_name=f"{company_id}_profit_and_loss.csv",
    mime="text/csv"
)


# =====================================================
# Financial Ratios
# =====================================================

st.divider()

st.subheader("📊 Financial Ratios")

display_ratios = annual_ratios.copy()

display_ratios = display_ratios.sort_values(
    "year",
    ascending=False
)

st.dataframe(
    display_ratios,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="📥 Download Financial Ratios CSV",
    data=display_ratios.to_csv(index=False),
    file_name=f"{company_id}_financial_ratios.csv",
    mime="text/csv"
)


# =====================================================
# Business Insights
# =====================================================

st.divider()

st.subheader("💡 Business Insights")

insights = []

if pd.notna(roe):

    if roe >= 20:
        insights.append(
            "✅ Strong Return on Equity indicates efficient use of shareholder capital."
        )
    elif roe >= 15:
        insights.append(
            "🟢 Healthy Return on Equity."
        )
    else:
        insights.append(
            "🟠 ROE is below the preferred benchmark."
        )


if pd.notna(debt):

    if debt < 0.5:
        insights.append(
            "✅ Low Debt-to-Equity suggests conservative leverage."
        )
    elif debt < 1:
        insights.append(
            "🟢 Debt level is manageable."
        )
    else:
        insights.append(
            "🔴 Company has relatively high leverage."
        )


if pd.notna(icr):

    if icr > 5:
        insights.append(
            "✅ Strong ability to cover interest obligations."
        )
    elif icr > 2:
        insights.append(
            "🟢 Interest coverage is acceptable."
        )
    else:
        insights.append(
            "🔴 Low Interest Coverage may indicate financial risk."
        )


if revenue > operating_profit > net_profit:

    insights.append(
        "✅ Profit structure appears financially consistent."
    )


for item in insights:

    st.success(item)


# =====================================================
# Dataset Information
# =====================================================

st.divider()

st.subheader("📂 Dataset Information")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Annual Reports",
        len(annual)
    )

with c2:

    st.metric(
        "Ratio Records",
        len(annual_ratios)
    )

with c3:

    st.metric(
        "Latest Year",
        latest_year
    )

with c4:

    st.metric(
        "Company",
        company_id
    )


# =====================================================
# Footer
# =====================================================

st.divider()

st.caption(
    "N100 Financial Intelligence Dashboard | Company Overview"
)