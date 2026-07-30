import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px
from dashboard.utils.db import (
    get_companies,
    get_trend_data
)

st.title("📈 Trend Analysis")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

company_id = companies[
    companies["company_name"] == selected_company
]["id"].iloc[0]

trend_df = get_trend_data(company_id)

# Remove rows where year is missing
trend_df = trend_df.dropna(subset=["year"])

st.subheader("Select Metrics")

metrics = st.multiselect(
    "Choose up to 3 metrics",
    [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "revenue_cagr_5y_pct",
        "pat_cagr_5y_pct",
        "interest_coverage",
        "free_cash_flow_cr",
        "composite_quality_score"
    ],
    default=["return_on_equity_pct"],
    max_selections=3
)

if metrics:

    fig = px.line(
        trend_df,
        x="year",
        y=metrics,
        markers=True,
        title="10-Year Trend Analysis"
    )

    # Add YoY labels
    for metric in metrics:

        yoy = trend_df[metric].pct_change() * 100

        for i in range(1, len(trend_df)):

            if (
                trend_df.iloc[i][metric] is not None
                and trend_df.iloc[i - 1][metric] is not None
            ):

                fig.add_annotation(
                    x=trend_df.iloc[i]["year"],
                    y=trend_df.iloc[i][metric],
                    text=f"{yoy.iloc[i]:.1f}%",
                    showarrow=False,
                    yshift=15,
                    font=dict(size=10)
                )

    st.plotly_chart(
        fig,
        use_container_width=True
    )