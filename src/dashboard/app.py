import streamlit as st

st.set_page_config(
    page_title="Nifty100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Nifty100 Financial Intelligence Platform")

st.markdown("---")

st.subheader("Welcome")

st.write(
    """
    This dashboard provides financial analysis for Nifty100 companies.

    Use the sidebar to navigate between pages.
    """
)

st.success("Dashboard loaded successfully!")