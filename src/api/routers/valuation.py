from fastapi import APIRouter, HTTPException
import sqlite3

from src.api.main import DB_PATH


router = APIRouter()


# ============================================================
# MARKET CAP / VALUATION HISTORY
# ============================================================

@router.get("/market-cap/{ticker}")
def get_market_cap_history(ticker: str):
    """
    Return historical valuation multiples for a company
    from 2019 to 2024.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. CHECK WHETHER COMPANY EXISTS
        # ----------------------------------------------------

        company_row = connection.execute(
            """
            SELECT
                id,
                company_name
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (ticker.upper(),),
        ).fetchone()

        if company_row is None:

            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        company_id = company_row["id"]

        # ----------------------------------------------------
        # 2. GET MARKET CAP HISTORY
        # ----------------------------------------------------

        rows = connection.execute(
            """
            SELECT
                year,
                market_cap_crore,
                enterprise_value_crore,
                pe_ratio,
                pb_ratio,
                ev_ebitda,
                dividend_yield_pct
            FROM market_cap
            WHERE company_id = ?
              AND year BETWEEN 2019 AND 2024
            ORDER BY year
            """,
            (company_id,),
        ).fetchall()

        # ----------------------------------------------------
        # 3. CHECK WHETHER DATA EXISTS
        # ----------------------------------------------------

        if not rows:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"No market cap data found for "
                    f"'{ticker}' from 2019 to 2024."
                ),
            )

        # ----------------------------------------------------
        # 4. BUILD HISTORY RESPONSE
        # ----------------------------------------------------

        history = []

        for row in rows:

            history.append({
                "year": row["year"],
                "market_cap_crore":
                    row["market_cap_crore"],
                "enterprise_value_crore":
                    row["enterprise_value_crore"],
                "pe_ratio":
                    row["pe_ratio"],
                "pb_ratio":
                    row["pb_ratio"],
                "ev_ebitda":
                    row["ev_ebitda"],
                "dividend_yield_pct":
                    row["dividend_yield_pct"],
            })

        # ----------------------------------------------------
        # 5. RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "company_id": company_id,
            "company_name": company_row["company_name"],
            "from_year": 2019,
            "to_year": 2024,
            "count": len(history),
            "history": history,
        }

    finally:

        connection.close()