import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px

from dashboard.utils.db import get_capital_data

# --------------------------------------------------
# Page Title
# --------------------------------------------------

st.title("🗺️ Capital Allocation Map")

# --------------------------------------------------
# Load Data
# --------------------------------------------------

df = get_capital_data()

if df.empty:
    st.warning("No data available.")
    st.stop()

# --------------------------------------------------
# Treemap
# --------------------------------------------------

fig = px.treemap(
    df,
    path=[
        "capital_allocation_pattern",
        "company_name"
    ],
    values="market_cap_crore",
    color="capital_allocation_pattern",
    hover_data=[
        "broad_sector",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow"
    ]
)

fig.update_layout(
    title="Capital Allocation Patterns"
)

st.plotly_chart(
    fig,
    width="stretch"
)