from typing import Optional
from pathlib import Path
import sqlite3

from fastapi import APIRouter, HTTPException, Query


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/screener",
    tags=["Screener"],
)


# ============================================================
# DATABASE PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# ============================================================
# SCREENER ENDPOINT
# ============================================================

@router.get("")
def screen_companies(
    min_roe: Optional[float] = Query(
        default=None,
        description="Minimum return on equity percentage.",
    ),
    max_de: Optional[float] = Query(
        default=None,
        description="Maximum debt-to-equity ratio.",
    ),
    min_fcf: Optional[float] = Query(
        default=None,
        description="Minimum free cash flow in crore.",
    ),
    sector: Optional[str] = Query(
        default=None,
        description="Filter by broad sector.",
    ),
    min_rev_cagr_5yr: Optional[float] = Query(
        default=None,
        description="Minimum 5-year revenue CAGR percentage.",
    ),
    min_pat_cagr_5yr: Optional[float] = Query(
        default=None,
        description="Minimum 5-year PAT CAGR percentage.",
    ),
    max_pe: Optional[float] = Query(
        default=None,
        description="Maximum P/E ratio.",
    ),
):
    """
    Screen companies using latest annual financial metrics.
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if min_roe is not None and min_roe < 0:
        raise HTTPException(
            status_code=400,
            detail="min_roe cannot be negative.",
        )

    if max_de is not None and max_de < 0:
        raise HTTPException(
            status_code=400,
            detail="max_de cannot be negative.",
        )

    if min_fcf is not None and min_fcf < 0:
        raise HTTPException(
            status_code=400,
            detail="min_fcf cannot be negative.",
        )

    if min_rev_cagr_5yr is not None and min_rev_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="min_rev_cagr_5yr cannot be less than -100.",
        )

    if min_pat_cagr_5yr is not None and min_pat_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="min_pat_cagr_5yr cannot be less than -100.",
        )

    if max_pe is not None and max_pe < 0:
        raise HTTPException(
            status_code=400,
            detail="max_pe cannot be negative.",
        )

    # ========================================================
    # DATABASE
    # ========================================================

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ====================================================
        # LATEST FINANCIAL RATIO FOR EACH COMPANY
        # ====================================================

        query = """
            SELECT
                c.id,
                c.company_name,
                c.broad_sector,
                c.sub_sector,
                c.market_cap_category,

                fr.year,

                fr.return_on_equity_pct AS roe_pct,
                fr.debt_to_equity AS debt_to_equity,
                fr.free_cash_flow_cr AS free_cash_flow_cr,

                fr.revenue_cagr_5y_pct AS revenue_cagr_5yr_pct,
                fr.pat_cagr_5y_pct AS pat_cagr_5yr_pct,

                mc.pe_ratio,

                fr.composite_quality_score

            FROM companies c

            INNER JOIN financial_ratios fr
                ON c.id = fr.company_id

            LEFT JOIN market_cap mc
                ON c.id = mc.company_id
                AND mc.year = fr.year

            WHERE fr.period_type = 'ANNUAL'

              AND fr.year = (
                  SELECT MAX(fr2.year)
                  FROM financial_ratios fr2
                  WHERE fr2.company_id = fr.company_id
                    AND fr2.period_type = 'ANNUAL'
              )
        """

        params = []

        # ====================================================
        # MIN ROE
        # ====================================================

        if min_roe is not None:

            query += """
                AND fr.return_on_equity_pct >= ?
            """

            params.append(min_roe)

        # ====================================================
        # MAX DEBT TO EQUITY
        # ====================================================

        if max_de is not None:

            query += """
                AND fr.debt_to_equity <= ?
            """

            params.append(max_de)

        # ====================================================
        # MIN FREE CASH FLOW
        # ====================================================

        if min_fcf is not None:

            query += """
                AND fr.free_cash_flow_cr >= ?
            """

            params.append(min_fcf)

        # ====================================================
        # SECTOR
        # ====================================================

        if sector:

            query += """
                AND LOWER(c.broad_sector) = LOWER(?)
            """

            params.append(sector)

        # ====================================================
        # MIN REVENUE CAGR
        # ====================================================

        if min_rev_cagr_5yr is not None:

            query += """
                AND fr.revenue_cagr_5y_pct >= ?
            """

            params.append(min_rev_cagr_5yr)

        # ====================================================
        # MIN PAT CAGR
        # ====================================================

        if min_pat_cagr_5yr is not None:

            query += """
                AND fr.pat_cagr_5y_pct >= ?
            """

            params.append(min_pat_cagr_5yr)

        # ====================================================
        # MAX P/E
        # ====================================================

        if max_pe is not None:

            query += """
                AND mc.pe_ratio <= ?
            """

            params.append(max_pe)

        # ====================================================
        # RANKING
        # ====================================================

        query += """
            ORDER BY
                fr.composite_quality_score DESC,
                fr.return_on_equity_pct DESC,
                fr.free_cash_flow_cr DESC
        """

        # ====================================================
        # EXECUTE
        # ====================================================

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:

        connection.close()

    # ========================================================
    # RESPONSE
    # ========================================================

    companies = [
        dict(row)
        for row in rows
    ]

    return {
        "count": len(companies),
        "filters": {
            "min_roe": min_roe,
            "max_de": max_de,
            "min_fcf": min_fcf,
            "sector": sector,
            "min_rev_cagr_5yr": min_rev_cagr_5yr,
            "min_pat_cagr_5yr": min_pat_cagr_5yr,
            "max_pe": max_pe,
        },
        "companies": companies,
    }