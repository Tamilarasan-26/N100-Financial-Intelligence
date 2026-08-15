import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.dashboard.utils.api import get_health


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nifty100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# TITLE
# ============================================================

st.title("📈 Nifty100 Financial Intelligence Platform")

st.markdown("---")


# ============================================================
# API HEALTH
# ============================================================

st.subheader("API Status")

try:

    health = get_health()

    if health["status"] == "ok":

        st.success(
            "FastAPI backend is connected successfully."
        )

    else:

        st.error(
            "FastAPI backend is not healthy."
        )

except Exception as error:

    st.error(
        f"Unable to connect to FastAPI: {error}"
    )


# ============================================================
# DATABASE SUMMARY
# ============================================================

if "health" in locals():

    st.subheader("Database Summary")

    row_counts = health.get(
        "db_row_counts",
        {}
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Companies",
            row_counts.get(
                "companies",
                0
            )
        )

    with col2:

        st.metric(
            "Financial Ratios",
            row_counts.get(
                "financial_ratios",
                0
            )
        )

    with col3:

        st.metric(
            "Market Cap Records",
            row_counts.get(
                "market_cap",
                0
            )
        )

    with col4:

        st.metric(
            "Stock Price Records",
            row_counts.get(
                "stock_prices",
                0
            )
        )


# ============================================================
# APPLICATION INFORMATION
# ============================================================

st.markdown("---")

st.subheader("Platform Information")

col1, col2 = st.columns(2)

with col1:

    st.write(
        f"**API Version:** "
        f"{health.get('version', 'Unknown')}"
    )

with col2:

    st.write(
        f"**API Status:** "
        f"{health.get('status', 'Unknown')}"
    )


st.info(
    "Use the sidebar to navigate between "
    "the Nifty100 analytics pages."
)