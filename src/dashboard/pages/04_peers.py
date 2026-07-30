import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.utils.db import (
    get_peer_groups,
    get_peer_companies
)

# ----------------------------------------------------
# Page Title
# ----------------------------------------------------

st.title("🤝 Peer Comparison")

# ----------------------------------------------------
# Load Peer Groups
# ----------------------------------------------------

sectors = get_peer_groups()

selected_sector = st.selectbox(
    "Select Sector",
    sectors["broad_sector"]
)

# ----------------------------------------------------
# Load Companies
# ----------------------------------------------------

peer_df = get_peer_companies(selected_sector)

st.subheader("Select Company")

if peer_df.empty:
    st.warning("No companies found for this sector.")
    st.stop()

selected_company = st.selectbox(
    "Choose Company",
    peer_df["company_name"]
)

company_data = peer_df[
    peer_df["company_name"] == selected_company
].iloc[0]

sector_average = peer_df.mean(numeric_only=True)

metric_columns = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "pe_ratio",
    "pb_ratio",
    "interest_coverage"
]

metric_labels = [
    "ROE",
    "ROCE",
    "Net Margin",
    "Debt/Equity",
    "Revenue CAGR",
    "P/E",
    "P/B",
    "Interest Coverage"
]

company_values = [
    0 if company_data[m] is None else company_data[m]
    for m in metric_columns
]

average_values = [
    0 if sector_average[m] is None else sector_average[m]
    for m in metric_columns
]

radar_labels = metric_labels + [metric_labels[0]]
radar_company = company_values + [company_values[0]]
radar_average = average_values + [average_values[0]]
fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=radar_company,
        theta=radar_labels,
        fill="toself",
        name=selected_company
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=radar_average,
        theta=radar_labels,
        fill="toself",
        name="Sector Average"
    )
)

fig.update_layout(
    title="📊 Company vs Sector Average",
    polar=dict(
        radialaxis=dict(
            visible=True,
            showline=True,
            gridcolor="lightgray"
        )
    ),
    showlegend=True,
    height=600
)

st.plotly_chart(
    fig,
    width="stretch"
)

# ----------------------------------------------------
# KPI Comparison Table
# ----------------------------------------------------

st.subheader("📊 KPI Comparison")

comparison_df = pd.DataFrame({
    "Metric": [
        "ROE",
        "ROCE",
        "Net Profit Margin",
        "Debt / Equity",
        "Revenue CAGR (5Y)",
        "P/E",
        "P/B",
        "Interest Coverage"
    ],

    selected_company: [
        company_data["return_on_equity_pct"],
        company_data["return_on_capital_employed_pct"],
        company_data["net_profit_margin_pct"],
        company_data["debt_to_equity"],
        company_data["revenue_cagr_5y_pct"],
        company_data["pe_ratio"],
        company_data["pb_ratio"],
        company_data["interest_coverage"]
    ],

    "Sector Average": [
        sector_average["return_on_equity_pct"],
        sector_average["return_on_capital_employed_pct"],
        sector_average["net_profit_margin_pct"],
        sector_average["debt_to_equity"],
        sector_average["revenue_cagr_5y_pct"],
        sector_average["pe_ratio"],
        sector_average["pb_ratio"],
        sector_average["interest_coverage"]
    ]
})

st.dataframe(
    comparison_df.round(2),
    width="stretch",
    hide_index=True
)   

# ----------------------------------------------------
# Show Company Count
# ----------------------------------------------------

st.subheader("🏢 Companies in Selected Sector")

st.write(f"Total Companies : {len(peer_df)}")

# ----------------------------------------------------
# Display Data
# ----------------------------------------------------

st.dataframe(
    peer_df,
    width="stretch"
)

