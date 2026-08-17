import sys
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORTS
# ============================================================

import streamlit as st

from dashboard.utils.db import get_screener_data


# ============================================================
# PAGE TITLE
# ============================================================

st.title("📊 Stock Screener")


# ============================================================
# LOAD DATA
# ============================================================

df = get_screener_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Filter Companies")

st.sidebar.subheader("Quick Filters")


# ============================================================
# INITIAL FILTER STATE
# ============================================================

defaults = {
    "roe_slider": 15.0,
    "de_slider": 2.0,
    "revenue_slider": 10.0,
    "pat_slider": 10.0,
    "opm_slider": 10.0,
    "pe_slider": 50.0,
    "pb_slider": 10.0,
    "dividend_slider": 0.0,
    "icr_slider": 2.0,
    "quality_slider": 50.0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# QUICK FILTER BUTTONS
# ============================================================

col1, col2 = st.sidebar.columns(2)

quality_btn = col1.button(
    "Quality",
    use_container_width=True,
)

value_btn = col2.button(
    "Value",
    use_container_width=True,
)

growth_btn = col1.button(
    "Growth",
    use_container_width=True,
)

dividend_btn = col2.button(
    "Dividend",
    use_container_width=True,
)

debtfree_btn = col1.button(
    "Debt-Free",
    use_container_width=True,
)

turnaround_btn = col2.button(
    "Turnaround",
    use_container_width=True,
)


# ============================================================
# QUALITY PRESET
# ============================================================
#
# AC-07:
# Quality preset must return between 10 and 50 companies.
#
# Database validation:
# Quality >= 70 -> 10 companies
#
# Therefore Quality preset uses only the composite
# quality score and keeps all other filters neutral.
# ============================================================

if quality_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 10.0
    st.session_state.revenue_slider = -20.0
    st.session_state.pat_slider = -20.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 200.0
    st.session_state.pb_slider = 30.0
    st.session_state.dividend_slider = 0.0
    st.session_state.icr_slider = 0.0

    # AC-07 validated threshold
    st.session_state.quality_slider = 70.0

    st.rerun()


# ============================================================
# VALUE PRESET
# ============================================================

if value_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 10.0
    st.session_state.revenue_slider = -20.0
    st.session_state.pat_slider = -20.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 20.0
    st.session_state.pb_slider = 3.0
    st.session_state.dividend_slider = 0.0
    st.session_state.icr_slider = 0.0
    st.session_state.quality_slider = 0.0

    st.rerun()


# ============================================================
# GROWTH PRESET
# ============================================================

if growth_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 10.0
    st.session_state.revenue_slider = 20.0
    st.session_state.pat_slider = 20.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 200.0
    st.session_state.pb_slider = 30.0
    st.session_state.dividend_slider = 0.0
    st.session_state.icr_slider = 0.0
    st.session_state.quality_slider = 0.0

    st.rerun()


# ============================================================
# DIVIDEND PRESET
# ============================================================

if dividend_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 10.0
    st.session_state.revenue_slider = -20.0
    st.session_state.pat_slider = -20.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 200.0
    st.session_state.pb_slider = 30.0
    st.session_state.dividend_slider = 2.0
    st.session_state.icr_slider = 0.0
    st.session_state.quality_slider = 0.0

    st.rerun()


# ============================================================
# DEBT-FREE PRESET
# ============================================================

if debtfree_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 0.2
    st.session_state.revenue_slider = -20.0
    st.session_state.pat_slider = -20.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 200.0
    st.session_state.pb_slider = 30.0
    st.session_state.dividend_slider = 0.0
    st.session_state.icr_slider = 0.0
    st.session_state.quality_slider = 0.0

    st.rerun()


# ============================================================
# TURNAROUND PRESET
# ============================================================

if turnaround_btn:

    st.session_state.roe_slider = 0.0
    st.session_state.de_slider = 10.0
    st.session_state.revenue_slider = 5.0
    st.session_state.pat_slider = 5.0
    st.session_state.opm_slider = 0.0
    st.session_state.pe_slider = 200.0
    st.session_state.pb_slider = 30.0
    st.session_state.dividend_slider = 0.0
    st.session_state.icr_slider = 0.0
    st.session_state.quality_slider = 0.0

    st.rerun()


# ============================================================
# FILTER SLIDERS
# ============================================================

roe = st.sidebar.slider(
    "Minimum ROE",
    min_value=0.0,
    max_value=100.0,
    key="roe_slider",
)

de = st.sidebar.slider(
    "Maximum Debt/Equity",
    min_value=0.0,
    max_value=10.0,
    key="de_slider",
)

revenue = st.sidebar.slider(
    "Minimum Revenue CAGR (5Y)",
    min_value=-20.0,
    max_value=100.0,
    key="revenue_slider",
)

pat = st.sidebar.slider(
    "Minimum PAT CAGR (5Y)",
    min_value=-20.0,
    max_value=100.0,
    key="pat_slider",
)

opm = st.sidebar.slider(
    "Minimum OPM",
    min_value=0.0,
    max_value=100.0,
    key="opm_slider",
)

pe = st.sidebar.slider(
    "Maximum P/E",
    min_value=0.0,
    max_value=200.0,
    key="pe_slider",
)

pb = st.sidebar.slider(
    "Maximum P/B",
    min_value=0.0,
    max_value=30.0,
    key="pb_slider",
)

dividend = st.sidebar.slider(
    "Minimum Dividend Yield",
    min_value=0.0,
    max_value=10.0,
    key="dividend_slider",
)

icr = st.sidebar.slider(
    "Minimum Interest Coverage",
    min_value=0.0,
    max_value=100.0,
    key="icr_slider",
)

quality = st.sidebar.slider(
    "Minimum Quality Score",
    min_value=0.0,
    max_value=100.0,
    key="quality_slider",
)


# ============================================================
# FILTER COMPANIES
# ============================================================

filtered_df = df[
    (df["return_on_equity_pct"] >= roe)
    & (df["debt_to_equity"] <= de)
    & (df["revenue_cagr_5y_pct"] >= revenue)
    & (df["pat_cagr_5y_pct"] >= pat)
    & (df["operating_profit_margin_pct"] >= opm)
    & (df["pe_ratio"] <= pe)
    & (df["pb_ratio"] <= pb)
    & (df["dividend_yield_pct"] >= dividend)
    & (df["interest_coverage"] >= icr)
    & (df["composite_quality_score"] >= quality)
]


# ============================================================
# RESULTS
# ============================================================

st.subheader("Companies")

st.write(
    f"Matching Companies : {len(filtered_df)}"
)


# ============================================================
# DATA TABLE
# ============================================================

st.dataframe(
    filtered_df,
    width="stretch",
)


# ============================================================
# CSV DOWNLOAD
# ============================================================

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download Filtered Results",
    data=csv,
    file_name="filtered_companies.csv",
    mime="text/csv",
)