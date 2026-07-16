import streamlit as st

st.set_page_config(
    page_title="N100 Financial Intelligence",
    page_icon="📈",
    layout="wide"
)

st.title("📈 N100 Financial Intelligence")

st.markdown(
    """
Welcome to the N100 Financial Intelligence Dashboard.

Use the navigation menu on the left to explore:

- 📊 Company Overview
- 📈 Financial Ratios
- 💰 Capital Allocation
- 🤝 Peer Comparison
- 🛡 Data Quality
"""
)

st.info("Select a page from the sidebar to begin.")