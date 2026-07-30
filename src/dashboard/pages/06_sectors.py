import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px

from dashboard.utils.db import (
    get_sector_data,
    get_sector_kpis
)

# ---------------------------------------------------
# Page Title
# ---------------------------------------------------

st.title("📊 Sector Analysis")

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------

df = get_sector_data()

# Remove missing values
df = df.dropna(
    subset=[
        "sales",
        "return_on_equity_pct",
        "market_cap_crore"
    ]
)

# ---------------------------------------------------
# Sector Filter
# ---------------------------------------------------

sector = st.selectbox(
    "Select Sector",
    sorted(df["broad_sector"].unique())
)

sector_df = df[
    df["broad_sector"] == sector
]

kpi_df = get_sector_kpis(sector)

# ---------------------------------------------------
# Bubble Chart
# ---------------------------------------------------

fig = px.scatter(

    sector_df,

    x="sales",

    y="return_on_equity_pct",

    size="market_cap_crore",

    color="sub_sector",

    hover_name="company_name",

    title=f"{sector} Sector",

    labels={
        "sales": "Revenue",
        "return_on_equity_pct": "ROE",
        "market_cap_crore": "Market Cap"
    }

)

st.plotly_chart(
    fig,
    width="stretch"
)

# ---------------------------------------------------
# Sector KPI Bar Chart
# ---------------------------------------------------

st.subheader("📈 Sector Median KPI")

if not kpi_df.empty:

    kpis = [
        "ROE",
        "ROCE",
        "Net Margin",
        "Debt/Equity",
        "Revenue CAGR"
    ]

    values = [
        kpi_df.iloc[0]["avg_roe"],
        kpi_df.iloc[0]["avg_roce"],
        kpi_df.iloc[0]["avg_margin"],
        kpi_df.iloc[0]["avg_de"],
        kpi_df.iloc[0]["avg_growth"]
    ]

    fig2 = px.bar(

        x=kpis,

        y=values,

        text=[round(v, 2) for v in values],

        labels={
            "x": "KPI",
            "y": "Average Value"
        },

        title=f"{sector} Sector KPIs"

    )

    fig2.update_traces(textposition="outside")

    st.plotly_chart(
        fig2,
        width="stretch"
    )