from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "nifty100.db"


# ---------------------------------------------------
# Load Companies
# ---------------------------------------------------
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


# ---------------------------------------------------
# Load Capital Allocation
# ---------------------------------------------------
@st.cache_data
def load_capital_allocation(company_id):

    conn = sqlite3.connect(DB_PATH)

    query = """
SELECT
    year,
    operating_activity,
    investing_activity,
    financing_activity,
    net_cash_flow,
    capital_allocation_pattern
FROM capital_allocation
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


# ---------------------------------------------------
# Streamlit Page
# ---------------------------------------------------
st.set_page_config(
    page_title="Capital Allocation",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Capital Allocation Dashboard")


companies = load_companies()

if companies.empty:

    st.error("No companies found.")

    st.stop()


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
st.sidebar.header("📌 Filters")

selected_company = st.sidebar.selectbox(
    "Select Company",
    companies["company_name"]
)

company = companies[
    companies["company_name"] == selected_company
].iloc[0]

company_id = company["id"]

st.header(company["company_name"])

st.caption(
    f"{company['broad_sector']} • "
    f"{company['market_cap_category']}"
)

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
    
st.divider()

capital = load_capital_allocation(company_id)

if capital.empty:

    st.warning(
        "No Capital Allocation data available."
    )

    st.stop()


latest = capital.iloc[-1]

capital = load_capital_allocation(company_id)

capital = (
    capital
    .sort_values("year")
    .drop_duplicates(
        subset="year",
        keep="last"
    )
)

# ---------------------------------------------------
# Latest Cash Flow KPIs
# ---------------------------------------------------

st.divider()

st.subheader("💰 Latest Cash Flow KPIs")

if capital.empty:

    st.warning("No Capital Allocation data available.")

else:

    latest = capital.iloc[-1]

    latest_year = int(latest["year"])

    operating_cf = latest["operating_activity"]
    investing_cf = latest["investing_activity"]
    financing_cf = latest["financing_activity"]
    net_cf = latest["net_cash_flow"]

    # Capital Allocation Pattern
    pattern = (
        latest["capital_allocation_pattern"]
        if "capital_allocation_pattern" in capital.columns
        else "N/A"
    )

    # ---------------- Financial Year ----------------

    col1, col2 = st.columns([4, 1])

    with col2:

        st.metric(
            "Financial Year",
            f"FY {latest_year}"
        )

    # ---------------- Row 1 ----------------

    row1 = st.columns(4)

    with row1[0]:

        st.metric(
            "Operating Cash Flow",
            f"₹ {operating_cf:,.0f} Cr"
        )

    with row1[1]:

        st.metric(
            "Investing Cash Flow",
            f"₹ {investing_cf:,.0f} Cr"
        )

    with row1[2]:

        st.metric(
            "Financing Cash Flow",
            f"₹ {financing_cf:,.0f} Cr"
        )

    with row1[3]:

        st.metric(
            "Net Cash Flow",
            f"₹ {net_cf:,.0f} Cr"
        )

    # ---------------- Row 2 ----------------

    st.markdown("### 📌 Capital Allocation Summary")

    summary1, summary2 = st.columns(2)

    with summary1:

        st.metric(
            "Allocation Pattern",
            pattern
        )

    with summary2:

        if net_cf > 0:

            st.success("Positive Net Cash Flow")

        elif net_cf < 0:

            st.error("Negative Net Cash Flow")

        else:

            st.info("Neutral Net Cash Flow")
            
# ---------------------------------------------------
# Cash Flow Trends
# ---------------------------------------------------

st.divider()

st.subheader("📈 Cash Flow Trends")

if capital.empty:

    st.warning("No Cash Flow Trend data available.")

else:

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "💰 Operating Cash Flow",
            "🏗 Investing Cash Flow",
            "🏦 Financing Cash Flow",
            "💵 Net Cash Flow"
        ]
    )

    # ---------------------------------------------------
    # Operating Cash Flow
    # ---------------------------------------------------

    with tab1:

        fig = px.line(
            capital,
            x="year",
            y="operating_activity",
            markers=True,
            title="Operating Cash Flow Trend"
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            xaxis_title="Financial Year",
            yaxis_title="Operating Cash Flow (₹ Cr)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------
    # Investing Cash Flow
    # ---------------------------------------------------

    with tab2:

        fig = px.line(
            capital,
            x="year",
            y="investing_activity",
            markers=True,
            title="Investing Cash Flow Trend"
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            xaxis_title="Financial Year",
            yaxis_title="Investing Cash Flow (₹ Cr)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------
    # Financing Cash Flow
    # ---------------------------------------------------

    with tab3:

        fig = px.line(
            capital,
            x="year",
            y="financing_activity",
            markers=True,
            title="Financing Cash Flow Trend"
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            xaxis_title="Financial Year",
            yaxis_title="Financing Cash Flow (₹ Cr)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ---------------------------------------------------
    # Net Cash Flow
    # ---------------------------------------------------

    with tab4:

        fig = px.line(
            capital,
            x="year",
            y="net_cash_flow",
            markers=True,
            title="Net Cash Flow Trend"
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            xaxis_title="Financial Year",
            yaxis_title="Net Cash Flow (₹ Cr)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        
# ---------------------------------------------------
# Capital Allocation Pattern Analysis
# ---------------------------------------------------

st.divider()

st.subheader("📊 Capital Allocation Pattern Analysis")

if (
    capital.empty
    or "capital_allocation_pattern" not in capital.columns
):

    st.warning(
        "Capital Allocation Pattern not available."
    )

else:

    pattern_counts = (
        capital["capital_allocation_pattern"]
        .value_counts()
        .reset_index()
    )

    pattern_counts.columns = [
        "Pattern",
        "Count"
    ]

    fig = px.bar(
        pattern_counts,
        x="Pattern",
        y="Count",
        color="Pattern",
        text="Count",
        title="Capital Allocation Pattern Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        showlegend=False,
        xaxis_title="Pattern",
        yaxis_title="Frequency"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ---------------------------------------------------
# Annual Capital Allocation Table
# ---------------------------------------------------

st.divider()

st.subheader("📋 Annual Capital Allocation")

st.dataframe(
    capital,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------------------
# Download CSV
# ---------------------------------------------------

csv = capital.to_csv(
    index=False
)

st.download_button(
    label="📥 Download Capital Allocation CSV",
    data=csv,
    file_name=f"{selected_company}_capital_allocation.csv",
    mime="text/csv"
)

# ---------------------------------------------------
# Financial Insights
# ---------------------------------------------------

st.divider()

st.subheader("💡 Financial Insights")

if not capital.empty:

    latest = capital.iloc[-1]

    operating = latest["operating_activity"]
    investing = latest["investing_activity"]
    financing = latest["financing_activity"]
    net_cash = latest["net_cash_flow"]

    if (
        "capital_allocation_pattern"
        in capital.columns
    ):
        pattern = latest[
            "capital_allocation_pattern"
        ]
    else:
        pattern = "Unknown"

    # Operating Cash Flow

    if operating > 0:

        st.success(
            "✅ Strong positive operating cash flow."
        )

    else:

        st.error(
            "❌ Weak operating cash flow."
        )

    # Investing

    if investing < 0:

        st.info(
            "📈 Company is actively investing for growth."
        )

    else:

        st.warning(
            "⚠ Low investment activity."
        )

    # Financing

    if financing < 0:

        st.success(
            "💰 Company is reducing financing obligations."
        )

    else:

        st.info(
            "🏦 Company is raising external capital."
        )

    # Net Cash

    if net_cash > 0:

        st.success(
            "✅ Positive net cash generation."
        )

    else:

        st.warning(
            "⚠ Negative net cash flow."
        )

    # Allocation Pattern

    st.info(
        f"📌 Capital Allocation Strategy: **{pattern}**"
    )