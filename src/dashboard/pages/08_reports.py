import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from dashboard.utils.db import (
    get_companies,
    get_annual_reports
)

st.title("📄 Annual Reports")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

company_id = companies.loc[
    companies["company_name"] == selected_company,
    "id"
].values[0]

reports = get_annual_reports(company_id)

# ----------------------------------------------------
# Show Reports
# ----------------------------------------------------

st.subheader("Available Annual Reports")

if reports.empty:
    st.warning("No annual reports available.")
    st.stop()

for _, row in reports.iterrows():

    year = row["year"]
    pdf = row["annual_report"]

    col1, col2 = st.columns([1, 4])

    with col1:
        st.write(f"**{year}**")

    with col2:

        if pdf and str(pdf).strip() != "":

            st.link_button(
                "📄 Open Annual Report",
                pdf
            )

        else:

            st.error("❌ Report Unavailable")