from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


# ==========================================================
# Database Path
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

DB_PATH = ROOT / "db" / "nifty100.db"


# ==========================================================
# Load Companies
# ==========================================================

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


# ==========================================================
# Load Peer Data
# ==========================================================

@st.cache_data
def load_peer_data(sector):

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT

        c.id,
        c.company_name,
        c.broad_sector,
        c.market_cap_category,

        f.year,
        f.period_type,

        f.return_on_equity_pct,
        f.return_on_capital_employed_pct,
        f.return_on_assets_pct,

        f.net_profit_margin_pct,
        f.operating_profit_margin_pct,

        f.asset_turnover,
        f.debt_to_equity,
        f.interest_coverage

    FROM companies c

    INNER JOIN financial_ratios f
        ON c.id = f.company_id

    WHERE
        c.broad_sector = ?
        AND f.period_type = 'ANNUAL'

    ORDER BY
        c.company_name,
        f.year
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(sector,)
    )

    conn.close()

    return df


# ==========================================================
# Streamlit Page
# ==========================================================

st.set_page_config(
    page_title="Peer Comparison Dashboard",
    page_icon="🤝",
    layout="wide"
)


# ==========================================================
# Page Title
# ==========================================================

st.title("🤝 Peer Comparison Dashboard")


# ==========================================================
# Load Companies
# ==========================================================

companies = load_companies()

if companies.empty:

    st.error("No companies found.")

    st.stop()


# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.header("📌 Filters")

selected_company = st.sidebar.selectbox(
    "Select Company",
    companies["company_name"]
)


# ==========================================================
# Selected Company
# ==========================================================

company = companies[
    companies["company_name"] == selected_company
].iloc[0]

company_id = company["id"]

sector = company["broad_sector"]

market_cap = company["market_cap_category"]


# ==========================================================
# Load Peer Companies
# ==========================================================

peer_data = load_peer_data(sector)


# ==========================================================
# Keep Latest Financial Year Only
# ==========================================================

if not peer_data.empty:

    latest_year = peer_data["year"].max()

    peer_data = peer_data[
        peer_data["year"] == latest_year
    ].copy()

else:

    latest_year = None

# ==========================================================
# Clean Invalid Financial Ratios
# ==========================================================

if not peer_data.empty:

    ratio_columns = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct"
    ]

    for col in ratio_columns:
        peer_data[col] = pd.to_numeric(
            peer_data[col],
            errors="coerce"
        )

    peer_data = peer_data[
        (
            peer_data["return_on_equity_pct"].between(-100, 100)
        ) &
        (
            peer_data["return_on_capital_employed_pct"].between(-100, 100)
        ) &
        (
            peer_data["return_on_assets_pct"].between(-100, 100)
        ) &
        (
            peer_data["net_profit_margin_pct"].between(-100, 100)
        ) &
        (
            peer_data["operating_profit_margin_pct"].between(-100, 100)
        )
    ].copy()


# ==========================================================
# Dashboard Header
# ==========================================================

st.header(selected_company)

st.caption(
    f"{sector} • {market_cap}"
)


# ==========================================================
# Company Information
# ==========================================================

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
        sector
    )

with c3:

    st.metric(
        "Market Cap",
        market_cap
    )


# ==========================================================
# Peer Summary
# ==========================================================

st.divider()

st.subheader("👥 Peer Group Summary")

left, right = st.columns([4, 1])

with left:

    st.info(
        f"Comparing **{selected_company}** with companies in the **{sector}** sector."
    )

with right:

    if latest_year:

        st.metric(
            "Financial Year",
            f"FY {latest_year}"
        )


# ==========================================================
# Peer Statistics
# ==========================================================

if not peer_data.empty:

    total_peers = peer_data["company_name"].nunique()

    # ------------------------------------------
    # Remove unrealistic outliers
    # ------------------------------------------

    filtered_roe = peer_data[
        peer_data["return_on_equity_pct"].between(-100, 100)
    ]

    filtered_roce = peer_data[
        peer_data["return_on_capital_employed_pct"].between(-100, 100)
    ]

    filtered_margin = peer_data[
        peer_data["net_profit_margin_pct"].between(-100, 100)
    ]

    # ------------------------------------------
    # Calculate averages
    # ------------------------------------------

    avg_roe = filtered_roe[
        "return_on_equity_pct"
    ].mean()

    avg_roce = filtered_roce[
        "return_on_capital_employed_pct"
    ].mean()

    avg_margin = filtered_margin[
        "net_profit_margin_pct"
    ].mean()

    r1, r2, r3, r4 = st.columns(4)

    with r1:

        st.metric(
            "Peer Companies",
            total_peers
        )

    with r2:

        st.metric(
            "Average ROE",
            f"{avg_roe:.2f}%"
        )

    with r3:

        st.metric(
            "Average ROCE",
            f"{avg_roce:.2f}%"
        )

    with r4:

        st.metric(
            "Average Net Margin",
            f"{avg_margin:.2f}%"
        )

else:

    st.warning(
        "No peer companies found."
    )

# ==========================================================
# Company Rank
# ==========================================================

st.divider()

st.subheader("🏆 Company Rank")

ranking_df = (
    peer_data
    .sort_values(
        by="return_on_equity_pct",
        ascending=False
    )
    .reset_index(drop=True)
)

ranking_df["Rank"] = ranking_df.index + 1

selected_rank = ranking_df[
    ranking_df["company_name"] == selected_company
]

if not selected_rank.empty:

    rank = int(selected_rank.iloc[0]["Rank"])

    total = len(ranking_df)

    c1, c2 = st.columns([1, 3])

    with c1:

        st.metric(
            "Rank",
            f"#{rank}"
        )

    with c2:

        st.success(
            f"**{selected_company}** ranks "
            f"**#{rank}** out of **{total}** peer companies "
            "based on Return on Equity (ROE)."
        )

# ==========================================================
# Sector Average Comparison
# ==========================================================

st.divider()

st.subheader("📊 Sector Average Comparison")

comparison = pd.DataFrame({

    "Metric": [
        "ROE",
        "ROCE",
        "ROA",
        "Net Margin",
        "Operating Margin"
    ],

    "Company": [

        peer_data.loc[
            peer_data["company_name"] == selected_company,
            "return_on_equity_pct"
        ].iloc[0],

        peer_data.loc[
            peer_data["company_name"] == selected_company,
            "return_on_capital_employed_pct"
        ].iloc[0],

        peer_data.loc[
            peer_data["company_name"] == selected_company,
            "return_on_assets_pct"
        ].iloc[0],

        peer_data.loc[
            peer_data["company_name"] == selected_company,
            "net_profit_margin_pct"
        ].iloc[0],

        peer_data.loc[
            peer_data["company_name"] == selected_company,
            "operating_profit_margin_pct"
        ].iloc[0]

    ],

    "Sector Average": [

        peer_data["return_on_equity_pct"].mean(),

        peer_data["return_on_capital_employed_pct"].mean(),

        peer_data["return_on_assets_pct"].mean(),

        peer_data["net_profit_margin_pct"].mean(),

        peer_data["operating_profit_margin_pct"].mean()

    ]

})
comparison["Status"] = comparison.apply(

    lambda row:
        "✅ Above Avg"
        if row["Company"] >= row["Sector Average"]
        else "🔻 Below Avg",

    axis=1

)
comparison["Company"] = comparison["Company"].map(
    lambda x: f"{x:.2f}%"
)

comparison["Sector Average"] = comparison["Sector Average"].map(
    lambda x: f"{x:.2f}%"
)
st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)
# ==========================================================
# Financial Insights
# ==========================================================

st.divider()

st.subheader("💡 Financial Insights")
roe_company = peer_data.loc[
    peer_data["company_name"] == selected_company,
    "return_on_equity_pct"
].iloc[0]

roe_avg = peer_data["return_on_equity_pct"].mean()

if roe_company >= roe_avg:
    st.success(
        f"🏆 ROE ({roe_company:.2f}%) is higher than the sector average ({roe_avg:.2f}%)."
    )
else:
    st.warning(
        f"ROE ({roe_company:.2f}%) is below the sector average ({roe_avg:.2f}%)."
    )
roce_company = peer_data.loc[
    peer_data["company_name"] == selected_company,
    "return_on_capital_employed_pct"
].iloc[0]

roce_avg = peer_data["return_on_capital_employed_pct"].mean()

if roce_company >= roce_avg:
    st.success(
        f"💰 ROCE ({roce_company:.2f}%) is above the sector average ({roce_avg:.2f}%)."
    )
else:
    st.warning(
        f"ROCE ({roce_company:.2f}%) is below the sector average ({roce_avg:.2f}%)."
    )
margin_company = peer_data.loc[
    peer_data["company_name"] == selected_company,
    "net_profit_margin_pct"
].iloc[0]

margin_avg = peer_data["net_profit_margin_pct"].mean()

if margin_company >= margin_avg:
    st.success(
        f"📈 Net Profit Margin ({margin_company:.2f}%) is better than the sector average."
    )
else:
    st.warning(
        f"Net Profit Margin ({margin_company:.2f}%) is below the sector average."
    )
op_company = peer_data.loc[
    peer_data["company_name"] == selected_company,
    "operating_profit_margin_pct"
].iloc[0]

op_avg = peer_data["operating_profit_margin_pct"].mean()

if op_company >= op_avg:
    st.success(
        f"🏭 Operating Margin ({op_company:.2f}%) is above the sector average."
    )
else:
    st.warning(
        f"Operating Margin ({op_company:.2f}%) is below the sector average."
    )
score = 0

if roe_company >= roe_avg:
    score += 1

if roce_company >= roce_avg:
    score += 1

if margin_company >= margin_avg:
    score += 1

if op_company >= op_avg:
    score += 1

if score == 4:
    st.success("🌟 Overall Performance: Excellent. The company outperforms its peers across all key profitability metrics.")
elif score >= 3:
    st.info("👍 Overall Performance: Strong. The company performs above average on most financial metrics.")
elif score >= 2:
    st.warning("⚖️ Overall Performance: Average. Some metrics are above average, while others need improvement.")
else:
    st.error("⚠️ Overall Performance: Below Average. The company trails its peers on several key metrics.")

# ==========================================================
# Top Industry Performers
# ==========================================================

st.divider()

st.subheader("🏆 Top Industry Performers")

highest_roe = peer_data.loc[
    peer_data["return_on_equity_pct"].idxmax()
]

highest_roce = peer_data.loc[
    peer_data["return_on_capital_employed_pct"].idxmax()
]

highest_roa = peer_data.loc[
    peer_data["return_on_assets_pct"].idxmax()
]

highest_margin = peer_data.loc[
    peer_data["net_profit_margin_pct"].idxmax()
]
c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "🏆 Highest ROE",
        highest_roe["company_name"],
        f'{highest_roe["return_on_equity_pct"]:.2f}%'
    )

with c2:

    st.metric(
        "💰 Highest ROCE",
        highest_roce["company_name"],
        f'{highest_roce["return_on_capital_employed_pct"]:.2f}%'
    )

with c3:

    st.metric(
        "📊 Highest ROA",
        highest_roa["company_name"],
        f'{highest_roa["return_on_assets_pct"]:.2f}%'
    )

with c4:

    st.metric(
        "📈 Highest Net Margin",
        highest_margin["company_name"],
        f'{highest_margin["net_profit_margin_pct"]:.2f}%'
    )

# ==========================================================
# Peer Data Preview
# ==========================================================

st.divider()

st.subheader("📋 Peer Data Preview")

preview = peer_data.copy()

st.dataframe(
    preview,
    use_container_width=True,
    hide_index=True
)
# ==========================================================
# Download Peer Comparison CSV
# ==========================================================

st.divider()

st.subheader("⬇ Download Peer Comparison Data")

download_df = peer_data.copy()

download_df = download_df[
    [
        "company_name",
        "year",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct"
    ]
]

download_df.columns = [
    "Company",
    "Year",
    "ROE (%)",
    "ROCE (%)",
    "ROA (%)",
    "Net Margin (%)",
    "Operating Margin (%)"
]

csv = download_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Peer Comparison CSV",
    data=csv,
    file_name=f"{selected_company}_Peer_Comparison.csv",
    mime="text/csv"
)

# ==========================================================
# Company Ranking
# ==========================================================

st.divider()

st.subheader("🏆 Company Ranking")

ranking = (
    peer_data
    .sort_values(
        by="return_on_equity_pct",
        ascending=False
    )
    .reset_index(drop=True)
)

ranking.index = ranking.index + 1

ranking = ranking[
    [
        "company_name",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct"
    ]
]

ranking.columns = [
    "Company",
    "ROE %",
    "ROCE %",
    "ROA %",
    "Net Margin %",
    "Operating Margin %"
]

st.dataframe(
    ranking.style.format({
        "ROE %": "{:.2f}",
        "ROCE %": "{:.2f}",
        "ROA %": "{:.2f}",
        "Net Margin %": "{:.2f}",
        "Operating Margin %": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True
)


# ==========================================================
# Peer Comparison Charts
# ==========================================================

st.divider()

st.subheader("📊 Peer Comparison Charts")

chart_df = peer_data.copy()

chart_df["Highlight"] = chart_df["company_name"].apply(
    lambda x: "Selected Company"
    if x == selected_company
    else "Peer Company"
)

color_map = {
    "Selected Company": "#ff7f0e",
    "Peer Company": "#4e79a7"
}

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏆 ROE",
        "📈 ROCE",
        "📊 ROA",
        "💰 Net Margin",
        "🏭 Operating Margin"
    ]
)

# ==========================================================
# ROE vs ROCE Scatter Plot
# ==========================================================

st.divider()

st.subheader("📈 ROE vs ROCE Performance")

scatter_df = chart_df.copy()

fig = px.scatter(
    scatter_df,
    x="return_on_equity_pct",
    y="return_on_capital_employed_pct",
    color="Highlight",
    text="company_name",
    color_discrete_map=color_map
)
fig.update_traces(
    marker=dict(
        size=18,
        line=dict(color="white", width=1)
    ),
    textposition="top center"
)
fig.add_vline(
    x=scatter_df["return_on_equity_pct"].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text="Avg ROE"
)

fig.add_hline(
    y=scatter_df["return_on_capital_employed_pct"].mean(),
    line_dash="dash",
    line_color="green",
    annotation_text="Avg ROCE"
)

fig.update_traces(
    marker=dict(
        sizemode="diameter",
        line=dict(width=1, color="white"),
        opacity=0.85
    )
)

fig.update_layout(
    template="plotly_dark",
    height=650,
    title="ROE vs ROCE Performance Matrix",
    xaxis_title="Return on Equity (%)",
    yaxis_title="Return on Capital Employed (%)"
    
)




st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# Company vs Sector Radar Chart
# ==========================================================

st.divider()

st.subheader("🕸 Company vs Sector Radar Chart")

# ----------------------------------------------------------
# Selected Company Metrics
# ----------------------------------------------------------

company_row = peer_data[
    peer_data["company_name"] == selected_company
].iloc[0]

# ----------------------------------------------------------
# Radar Metrics
# ----------------------------------------------------------

metrics = [
    "ROE",
    "ROCE",
    "ROA",
    "Net Margin",
    "Operating Margin"
]

company_values = [
    company_row["return_on_equity_pct"],
    company_row["return_on_capital_employed_pct"],
    company_row["return_on_assets_pct"],
    company_row["net_profit_margin_pct"],
    company_row["operating_profit_margin_pct"]
]

sector_values = [
    peer_data["return_on_equity_pct"].mean(),
    peer_data["return_on_capital_employed_pct"].mean(),
    peer_data["return_on_assets_pct"].mean(),
    peer_data["net_profit_margin_pct"].mean(),
    peer_data["operating_profit_margin_pct"].mean()
]

# Close the radar polygon

metrics_closed = metrics + [metrics[0]]

company_closed = company_values + [company_values[0]]

sector_closed = sector_values + [sector_values[0]]

# ----------------------------------------------------------
# Radar Chart
# ----------------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_closed,
        theta=metrics_closed,
        fill="toself",
        name=selected_company,
        line=dict(width=3),
        opacity=0.8
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=sector_closed,
        theta=metrics_closed,
        fill="toself",
        name="Sector Average",
        line=dict(width=3),
        opacity=0.5
    )
)

fig.update_layout(

    template="plotly_dark",

    height=650,

    title="Company vs Sector Profitability Comparison",

    polar=dict(

        radialaxis=dict(
            visible=True,
            showline=True,
            gridcolor="gray"
        )

    ),

    legend=dict(
        orientation="h",
        y=1.08,
        x=0.5,
        xanchor="center"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# Financial Metrics Correlation Heatmap
# ==========================================================

st.divider()

st.subheader("🔥 Financial Metrics Correlation Heatmap")

# ----------------------------------------------------------
# Select Numerical Metrics
# ----------------------------------------------------------

corr_df = peer_data[
    [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "asset_turnover",
        "debt_to_equity",
        "interest_coverage"
    ]
].copy()

# ----------------------------------------------------------
# Remove Missing Values
# ----------------------------------------------------------

corr_df = corr_df.dropna()

# ----------------------------------------------------------
# Rename Columns
# ----------------------------------------------------------

corr_df.columns = [
    "ROE",
    "ROCE",
    "ROA",
    "Net Margin",
    "Operating Margin",
    "Asset Turnover",
    "Debt/Equity",
    "Interest Coverage"
]

# ----------------------------------------------------------
# Correlation Matrix
# ----------------------------------------------------------

corr = corr_df.corr().round(2)

# ----------------------------------------------------------
# Heatmap
# ----------------------------------------------------------

fig = px.imshow(
    corr,

    text_auto=".2f",

    color_continuous_scale="RdBu_r",

    zmin=-1,

    zmax=1,

    aspect="auto",

    title="Correlation Between Financial Metrics"
)

# ----------------------------------------------------------
# Layout
# ----------------------------------------------------------

fig.update_layout(

    template="plotly_dark",

    height=700,

    title_x=0.5,

    font=dict(
        size=13
    ),

    coloraxis_colorbar=dict(
        title="Correlation"
    )
)

# ----------------------------------------------------------
# Display
# ----------------------------------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# Financial Metrics Distribution (Box Plot Analysis)
# ==========================================================

st.divider()

st.header("📦 Financial Metrics Distribution")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏆 ROE",
        "📈 ROCE",
        "📊 ROA",
        "💰 Net Margin",
        "🏭 Operating Margin"
    ]
)

# ==========================================================
# ROE Distribution
# ==========================================================

with tab1:

    fig = px.box(
        chart_df,
        y="return_on_equity_pct",
        color="Highlight",
        color_discrete_map=color_map,
        points="all",
        hover_name="company_name",
        title="Return on Equity Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis_title="ROE (%)",
        xaxis_title="",
        legend_title="",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# ROCE Distribution
# ==========================================================

with tab2:

    fig = px.box(
        chart_df,
        y="return_on_capital_employed_pct",
        color="Highlight",
        color_discrete_map=color_map,
        points="all",
        hover_name="company_name",
        title="Return on Capital Employed Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis_title="ROCE (%)",
        xaxis_title="",
        legend_title="",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# ROA Distribution
# ==========================================================

with tab3:

    fig = px.box(
        chart_df,
        y="return_on_assets_pct",
        color="Highlight",
        color_discrete_map=color_map,
        points="all",
        hover_name="company_name",
        title="Return on Assets Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis_title="ROA (%)",
        xaxis_title="",
        legend_title="",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# Net Profit Margin Distribution
# ==========================================================

with tab4:

    fig = px.box(
        chart_df,
        y="net_profit_margin_pct",
        color="Highlight",
        color_discrete_map=color_map,
        points="all",
        hover_name="company_name",
        title="Net Profit Margin Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis_title="Net Margin (%)",
        xaxis_title="",
        legend_title="",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================================
# Operating Profit Margin Distribution
# ==========================================================

with tab5:

    fig = px.box(
        chart_df,
        y="operating_profit_margin_pct",
        color="Highlight",
        color_discrete_map=color_map,
        points="all",
        hover_name="company_name",
        title="Operating Profit Margin Distribution"
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        yaxis_title="Operating Margin (%)",
        xaxis_title="",
        legend_title="",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



# ==========================================================
# Operating Margin
# ==========================================================

with tab5:

    fig = px.bar(
        chart_df.sort_values(
            "operating_profit_margin_pct",
            ascending=False
        ),
        x="company_name",
        y="operating_profit_margin_pct",
        color="Highlight",
        color_discrete_map=color_map,
        text="operating_profit_margin_pct",
        title="Operating Profit Margin Comparison"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_dark",
        height=550,
        xaxis_title="Company",
        yaxis_title="Operating Margin (%)",
        legend_title="",
        xaxis_tickangle=-35
    )

    st.plotly_chart(fig, use_container_width=True)
    
# ==========================================================
# Executive Summary Dashboard
# ==========================================================

st.divider()

st.header("📋 Executive Summary Dashboard")

# ----------------------------------------------------------
# Company Metrics
# ----------------------------------------------------------

company_roe = roe_company
company_roce = roce_company
company_margin = margin_company
company_op_margin = op_company

company_roa = peer_data.loc[
    peer_data["company_name"] == selected_company,
    "return_on_assets_pct"
].iloc[0]

avg_roa = peer_data["return_on_assets_pct"].mean()

# ----------------------------------------------------------
# Performance Score
# ----------------------------------------------------------

score = 0

if company_roe >= roe_avg:
    score += 20

if company_roce >= roce_avg:
    score += 20

if company_roa >= avg_roa:
    score += 20

if company_margin >= margin_avg:
    score += 20

if company_op_margin >= op_avg:
    score += 20

# ----------------------------------------------------------
# Overall Score
# ----------------------------------------------------------

left, right = st.columns([1,3])

with left:

    st.metric(
        "Overall Score",
        f"{score}/100"
    )

with right:

    if score >= 80:

        st.success(
            "🏆 Excellent Financial Performance"
        )

    elif score >= 60:

        st.info(
            "👍 Good Financial Performance"
        )

    elif score >= 40:

        st.warning(
            "⚠ Average Financial Performance"
        )

    else:

        st.error(
            "❌ Needs Improvement"
        )

# ----------------------------------------------------------
# Performance Grade
# ----------------------------------------------------------

if score >= 90:
    grade = "A+"

elif score >= 80:
    grade = "A"

elif score >= 70:
    grade = "B"

elif score >= 60:
    grade = "C"

else:
    grade = "D"

st.metric(
    "Performance Grade",
    grade
)

# ----------------------------------------------------------
# Strengths
# ----------------------------------------------------------

st.subheader("✅ Key Strengths")

strengths = []

if company_roe >= roe_avg:
    strengths.append(
        f"Strong ROE ({company_roe:.2f}%) exceeds the sector average."
    )

if company_roce >= roce_avg:
    strengths.append(
        f"High ROCE ({company_roce:.2f}%) indicates efficient capital utilization."
    )

if company_roa >= avg_roa:
    strengths.append(
        f"ROA ({company_roa:.2f}%) is above the industry average."
    )

if company_margin >= margin_avg:
    strengths.append(
        f"Healthy Net Profit Margin ({company_margin:.2f}%)."
    )

if company_op_margin >= op_avg:
    strengths.append(
        f"Strong Operating Margin ({company_op_margin:.2f}%)."
    )

if strengths:

    for item in strengths:

        st.success(item)

else:

    st.warning(
        "No major strengths identified."
    )

# ----------------------------------------------------------
# Areas for Improvement
# ----------------------------------------------------------

st.subheader("⚠ Areas for Improvement")

weaknesses = []

if company_roe < roe_avg:
    weaknesses.append("Improve Return on Equity.")

if company_roce < roce_avg:
    weaknesses.append("Improve Return on Capital Employed.")

if company_roa < avg_roa:
    weaknesses.append("Improve Asset Utilization.")

if company_margin < margin_avg:
    weaknesses.append("Increase Net Profit Margin.")

if company_op_margin < op_avg:
    weaknesses.append("Improve Operating Margin.")

if weaknesses:

    for item in weaknesses:

        st.warning(item)

else:

    st.success(
        "No major weaknesses detected."
    )

# ----------------------------------------------------------
# Final Investment View
# ----------------------------------------------------------

st.subheader("💡 Investment View")

if score >= 80:

    st.success(
        f"{selected_company} demonstrates excellent profitability and outperforms most companies in the {sector} sector."
    )

elif score >= 60:

    st.info(
        f"{selected_company} performs above average with strong financial fundamentals."
    )

elif score >= 40:

    st.warning(
        f"{selected_company} performs close to the sector average."
    )

else:

    st.error(
        f"{selected_company} underperforms compared with its sector peers."
    )

# ----------------------------------------------------------
# Recommendation
# ----------------------------------------------------------

st.subheader("🎯 Recommendation")

if score >= 80:

    st.success(
        "Strong Buy Candidate (Based only on profitability metrics)"
    )

elif score >= 60:

    st.info(
        "Good Company to Watch"
    )

elif score >= 40:

    st.warning(
        "Neutral Recommendation"
    )

else:

    st.error(
        "Requires Further Financial Analysis"
    )