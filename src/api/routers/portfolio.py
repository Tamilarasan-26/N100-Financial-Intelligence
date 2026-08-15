from fastapi import APIRouter, HTTPException
import sqlite3
import math

from src.api.main import DB_PATH


router = APIRouter()


# ============================================================
# HELPER FUNCTION
# ============================================================

def calculate_percentile(values, percentile):
    """
    Calculate a percentile using linear interpolation.
    """

    if not values:
        return None

    values = sorted(values)

    if len(values) == 1:
        return round(values[0], 2)

    position = (len(values) - 1) * (percentile / 100)

    lower_index = math.floor(position)
    upper_index = math.ceil(position)

    if lower_index == upper_index:
        return round(values[lower_index], 2)

    lower_value = values[lower_index]
    upper_value = values[upper_index]

    result = lower_value + (
        upper_value - lower_value
    ) * (position - lower_index)

    return round(result, 2)


# ============================================================
# GET PORTFOLIO STATISTICS
# ============================================================

@router.get("/portfolio/stats")
def get_portfolio_stats():
    """
    Return P10 through P90 percentile statistics
    for 10 core financial KPIs across all companies.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. GET LATEST FINANCIAL YEAR FOR EACH COMPANY
        # ----------------------------------------------------

        query = """
        WITH latest_ratios AS (
            SELECT
                fr.company_id,
                fr.year,

                fr.return_on_equity_pct,
                fr.return_on_capital_employed_pct,
                fr.net_profit_margin_pct,
                fr.debt_to_equity,
                fr.interest_coverage,
                fr.asset_turnover,
                fr.revenue_cagr_5y_pct,
                fr.pat_cagr_5y_pct,
                fr.eps_cagr_5y_pct,
                fr.free_cash_flow_cr

            FROM financial_ratios fr

            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM financial_ratios
                GROUP BY company_id
            ) latest

                ON fr.company_id = latest.company_id
                AND fr.year = latest.latest_year
        )

        SELECT
            company_id,
            year,

            return_on_equity_pct,
            return_on_capital_employed_pct,
            net_profit_margin_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            revenue_cagr_5y_pct,
            pat_cagr_5y_pct,
            eps_cagr_5y_pct,
            free_cash_flow_cr

        FROM latest_ratios

        ORDER BY company_id
        """

        rows = connection.execute(query).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No financial ratio data found."
            )

        # ----------------------------------------------------
        # 2. DEFINE 10 CORE KPIs
        # ----------------------------------------------------

        kpi_columns = {
            "ROE": "return_on_equity_pct",
            "ROCE": "return_on_capital_employed_pct",
            "Net Profit Margin": "net_profit_margin_pct",
            "Debt To Equity": "debt_to_equity",
            "Interest Coverage": "interest_coverage",
            "Asset Turnover": "asset_turnover",
            "Revenue CAGR 5Y": "revenue_cagr_5y_pct",
            "PAT CAGR 5Y": "pat_cagr_5y_pct",
            "EPS CAGR 5Y": "eps_cagr_5y_pct",
            "Free Cash Flow": "free_cash_flow_cr",
        }

        # ----------------------------------------------------
        # 3. CALCULATE PERCENTILES
        # ----------------------------------------------------

        statistics = []

        for metric_name, column_name in kpi_columns.items():

            values = []

            for row in rows:

                value = row[column_name]

                if value is not None:

                    try:
                        value = float(value)

                        if math.isfinite(value):
                            values.append(value)

                    except (TypeError, ValueError):
                        continue

            if not values:
                statistics.append({
                    "metric": metric_name,
                    "company_count": 0,
                    "p10": None,
                    "p20": None,
                    "p30": None,
                    "p40": None,
                    "p50": None,
                    "p60": None,
                    "p70": None,
                    "p80": None,
                    "p90": None,
                })

                continue

            statistics.append({
                "metric": metric_name,
                "company_count": len(values),

                "p10": calculate_percentile(
                    values, 10
                ),

                "p20": calculate_percentile(
                    values, 20
                ),

                "p30": calculate_percentile(
                    values, 30
                ),

                "p40": calculate_percentile(
                    values, 40
                ),

                "p50": calculate_percentile(
                    values, 50
                ),

                "p60": calculate_percentile(
                    values, 60
                ),

                "p70": calculate_percentile(
                    values, 70
                ),

                "p80": calculate_percentile(
                    values, 80
                ),

                "p90": calculate_percentile(
                    values, 90
                ),
            })

        # ----------------------------------------------------
        # 4. DETERMINE LATEST YEAR
        # ----------------------------------------------------

        latest_year = max(
            row["year"]
            for row in rows
            if row["year"] is not None
        )

        # ----------------------------------------------------
        # 5. RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "year": latest_year,
            "company_count": len(rows),
            "metric_count": len(statistics),
            "percentiles": statistics,
        }

    finally:

        connection.close()