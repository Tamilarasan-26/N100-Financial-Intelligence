import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from dashboard.utils.db import get_screener_data

st.title("📊 Stock Screener")

df = get_screener_data()

# Remove rows with missing values in filter columns
df = df.dropna(
    subset=[
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5y_pct",
        "pat_cagr_5y_pct",
        "operating_profit_margin_pct",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield_pct",
        "interest_coverage",
        "composite_quality_score"
    ]
)

st.sidebar.header("Filter Companies")

st.sidebar.subheader("Quick Filters")

col1, col2 = st.sidebar.columns(2)

quality_btn = col1.button("Quality")
value_btn = col2.button("Value")

growth_btn = col1.button("Growth")
dividend_btn = col2.button("Dividend")

debtfree_btn = col1.button("Debt-Free")
turnaround_btn = col2.button("Turnaround")

roe_default = 15.0
de_default = 2.0
revenue_default = 10.0
pat_default = 10.0
opm_default = 10.0
pe_default = 50.0
pb_default = 10.0
dividend_default = 0.0
icr_default = 2.0
quality_default = 50.0

if quality_btn:
    roe_default = 20
    de_default = 1
    quality_default = 80

elif value_btn:
    pe_default = 20
    pb_default = 3

elif growth_btn:
    revenue_default = 20
    pat_default = 20

elif dividend_btn:
    dividend_default = 2

elif debtfree_btn:
    de_default = 0.2

elif turnaround_btn:
    revenue_default = 5
    pat_default = 5

roe = st.sidebar.slider(
    "Minimum ROE",
    0.0,
    100.0,
    15.0
)

de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    10.0,
    2.0
)

revenue = st.sidebar.slider(
    "Minimum Revenue CAGR (5Y)",
    -20.0,
    100.0,
    10.0
)

pat = st.sidebar.slider(
    "Minimum PAT CAGR (5Y)",
    -20.0,
    100.0,
    10.0
)

opm = st.sidebar.slider(
    "Minimum OPM",
    0.0,
    100.0,
    10.0
)

pe = st.sidebar.slider(
    "Maximum P/E",
    0.0,
    200.0,
    50.0
)

pb = st.sidebar.slider(
    "Maximum P/B",
    0.0,
    30.0,
    10.0
)

dividend = st.sidebar.slider(
    "Minimum Dividend Yield",
    0.0,
    10.0,
    0.0
)

icr = st.sidebar.slider(
    "Minimum Interest Coverage",
    0.0,
    100.0,
    2.0
)

quality = st.sidebar.slider(
    "Minimum Quality Score",
    0.0,
    100.0,
    50.0
)

filtered_df = df[
    (df["return_on_equity_pct"] >= roe) &
    (df["debt_to_equity"] <= de) &
    (df["revenue_cagr_5y_pct"] >= revenue) &
    (df["pat_cagr_5y_pct"] >= pat) &
    (df["operating_profit_margin_pct"] >= opm) &
    (df["pe_ratio"] <= pe) &
    (df["pb_ratio"] <= pb) &
    (df["dividend_yield_pct"] >= dividend) &
    (df["interest_coverage"] >= icr) &
    (df["composite_quality_score"] >= quality)
]

st.subheader("Companies")

st.write(f"Matching Companies : {len(filtered_df)}")

st.dataframe(
    filtered_df,
    width="stretch"
)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Results",
    data=csv,
    file_name="filtered_companies.csv",
    mime="text/csv"
)