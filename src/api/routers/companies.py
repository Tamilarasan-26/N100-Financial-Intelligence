import sqlite3
from pathlib import Path
from typing import Optional


from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# ============================================================
# GET ALL COMPANIES
# ============================================================

@router.get("")
def get_companies(
    sector: Optional[str] = Query(
        default=None,
        description="Filter companies by broad sector.",
    ),
    market_cap_category: Optional[str] = Query(
        default=None,
        description="Filter companies by market-cap category.",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search by company name or company ID.",
    ),
):
    """
    Return the list of Nifty 100 companies with optional filters.
    """

    query = """
        SELECT
            id,
            company_name,
            broad_sector,
            sub_sector,
            roe_percentage AS roe_pct,
            roce_percentage AS roce_pct,
            market_cap_category
        FROM companies
        WHERE 1 = 1
    """

    params = []

    # --------------------------------------------------------
    # Sector filter
    # --------------------------------------------------------

    if sector:
        query += """
            AND broad_sector = ?
        """

        params.append(sector)

    # --------------------------------------------------------
    # Market-cap filter
    # --------------------------------------------------------

    if market_cap_category:
        query += """
            AND market_cap_category = ?
        """

        params.append(market_cap_category)

    # --------------------------------------------------------
    # Search filter
    # --------------------------------------------------------

    if search:
        query += """
            AND (
                company_name LIKE ?
                OR id LIKE ?
            )
        """

        search_pattern = f"%{search}%"

        params.extend(
            [
                search_pattern,
                search_pattern,
            ]
        )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    query += """
        ORDER BY company_name
    """

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:
        connection.close()

    # --------------------------------------------------------
    # Convert rows to dictionaries
    # --------------------------------------------------------

    companies = [
        dict(row)
        for row in rows
    ]

    return {
        "count": len(companies),
        "companies": companies,
    }


# ============================================================
# GET COMPANY PROFILE
# ============================================================

@router.get("/{company_id}")
def get_company_profile(
    company_id: str,
):
    """
    Return a complete company profile with the latest
    annual financial ratios.
    """

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:

        # ====================================================
        # COMPANY INFORMATION
        # ====================================================

        company_row = connection.execute(
            """
            SELECT
                id,
                company_logo,
                company_name,
                chart_link,
                about_company,
                website,
                nse_profile,
                bse_profile,
                face_value,
                book_value,
                roce_percentage,
                roe_percentage,
                broad_sector,
                sub_sector,
                index_weight_pct,
                market_cap_category
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()

        # ====================================================
        # COMPANY NOT FOUND
        # ====================================================

        if company_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found.",
            )

        # ====================================================
        # LATEST ANNUAL FINANCIAL RATIOS
        # ====================================================

        ratio_row = connection.execute(
            """
            SELECT
                year,
                period_type,
                period_months,

                net_profit_margin_pct,
                operating_profit_margin_pct,

                return_on_equity_pct,
                return_on_capital_employed_pct,
                return_on_assets_pct,

                debt_to_equity,
                high_leverage_flag,

                interest_coverage,
                icr_label,
                low_interest_coverage_flag,

                net_debt_cr,
                asset_turnover,

                revenue_cagr_3y_pct,
                revenue_cagr_3y_flag,

                revenue_cagr_5y_pct,
                revenue_cagr_5y_flag,

                revenue_cagr_10y_pct,
                revenue_cagr_10y_flag,

                pat_cagr_3y_pct,
                pat_cagr_3y_flag,

                pat_cagr_5y_pct,
                pat_cagr_5y_flag,

                pat_cagr_10y_pct,
                pat_cagr_10y_flag,

                eps_cagr_3y_pct,
                eps_cagr_3y_flag,

                eps_cagr_5y_pct,
                eps_cagr_5y_flag,

                eps_cagr_10y_pct,
                eps_cagr_10y_flag,

                free_cash_flow_cr,

                cfo_quality_score,
                cfo_quality_label,

                capex_cr,
                capex_intensity_pct,

                fcf_conversion_rate_pct,

                earnings_per_share,
                book_value_per_share,

                dividend_payout_ratio_pct,

                total_debt_cr,
                cash_from_operations_cr,

                composite_quality_score

            FROM financial_ratios

            WHERE company_id = ?
              AND period_type = 'ANNUAL'

            ORDER BY year DESC

            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

    finally:
        connection.close()

    # ========================================================
    # CONVERT DATABASE ROWS TO DICTIONARIES
    # ========================================================

    company = dict(company_row)

    latest_ratios = (
        dict(ratio_row)
        if ratio_row is not None
        else None
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "company": company,
        "latest_ratios": latest_ratios,
    }
# ============================================================
# GET COMPANY PROFIT & LOSS
# ============================================================

@router.get("/{company_id}/pl")
def get_company_profit_and_loss(
    company_id: str,
    from_year: Optional[int] = Query(
        default=None,
        description="Starting year for the annual P&L history.",
    ),
    to_year: Optional[int] = Query(
        default=None,
        description="Ending year for the annual P&L history.",
    ),
):
    """
    Return annual profit-and-loss history for a company.
    """

    # --------------------------------------------------------
    # Validate year range
    # --------------------------------------------------------

    if (
        from_year is not None
        and to_year is not None
        and from_year > to_year
    ):
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year.",
        )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # Verify company exists
        # ----------------------------------------------------

        company_exists = connection.execute(
            """
            SELECT 1
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        if company_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found.",
            )

        # ----------------------------------------------------
        # Build query
        # ----------------------------------------------------

        query = """
            SELECT
                company_id,
                year,
                period_type,
                period_months,
                sales,
                expenses,
                operating_profit,
                opm_percentage,
                other_income,
                interest,
                depreciation,
                profit_before_tax,
                tax_percentage,
                net_profit,
                eps,
                dividend_payout
            FROM profitandloss
            WHERE company_id = ?
              AND period_type = 'ANNUAL'
        """

        params = [company_id]

        # ----------------------------------------------------
        # From-year filter
        # ----------------------------------------------------

        if from_year is not None:
            query += """
                AND year >= ?
            """

            params.append(from_year)

        # ----------------------------------------------------
        # To-year filter
        # ----------------------------------------------------

        if to_year is not None:
            query += """
                AND year <= ?
            """

            params.append(to_year)

        # ----------------------------------------------------
        # Sort newest → oldest
        # ----------------------------------------------------

        query += """
            ORDER BY year DESC
        """

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:
        connection.close()

    # --------------------------------------------------------
    # Convert rows
    # --------------------------------------------------------

    records = [
        dict(row)
        for row in rows
    ]

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "company_id": company_id,
        "count": len(records),
        "from_year": from_year,
        "to_year": to_year,
        "data": records,
    }
    
# ============================================================
# GET COMPANY BALANCE SHEET
# ============================================================

@router.get("/{company_id}/bs")
def get_company_balance_sheet(
    company_id: str,
    from_year: Optional[int] = Query(
        default=None,
        description="Starting year for the balance-sheet history.",
    ),
    to_year: Optional[int] = Query(
        default=None,
        description="Ending year for the balance-sheet history.",
    ),
):
    """
    Return balance-sheet history for a company.
    """

    # --------------------------------------------------------
    # Validate year range
    # --------------------------------------------------------

    if (
        from_year is not None
        and to_year is not None
        and from_year > to_year
    ):
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year.",
        )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # Verify company exists
        # ----------------------------------------------------

        company_exists = connection.execute(
            """
            SELECT 1
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        if company_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found.",
            )

        # ----------------------------------------------------
        # Build query
        # ----------------------------------------------------

        query = """
            SELECT
                company_id,
                year,
                equity_capital,
                reserves,
                borrowings,
                other_liabilities,
                total_liabilities,
                fixed_assets,
                cwip,
                investments,
                other_asset,
                total_assets
            FROM balancesheet
            WHERE company_id = ?
        """

        params = [company_id]

        # ----------------------------------------------------
        # From-year filter
        # ----------------------------------------------------

        if from_year is not None:
            query += """
                AND year >= ?
            """

            params.append(from_year)

        # ----------------------------------------------------
        # To-year filter
        # ----------------------------------------------------

        if to_year is not None:
            query += """
                AND year <= ?
            """

            params.append(to_year)

        # ----------------------------------------------------
        # Sort newest → oldest
        # ----------------------------------------------------

        query += """
            ORDER BY year DESC, id DESC
        """

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:
        connection.close()

    # --------------------------------------------------------
    # Convert rows to dictionaries
    # --------------------------------------------------------

    records = [
        dict(row)
        for row in rows
    ]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "company_id": company_id,
        "count": len(records),
        "from_year": from_year,
        "to_year": to_year,
        "data": records,
    }
    
# ============================================================
# GET COMPANY CASH FLOW
# ============================================================

@router.get("/{company_id}/cashflow")
def get_company_cash_flow(
    company_id: str,
    from_year: Optional[int] = Query(
        default=None,
        description="Starting year for the cash-flow history.",
    ),
    to_year: Optional[int] = Query(
        default=None,
        description="Ending year for the cash-flow history.",
    ),
):
    """
    Return annual cash-flow history for a company.
    """

    # --------------------------------------------------------
    # Validate year range
    # --------------------------------------------------------

    if (
        from_year is not None
        and to_year is not None
        and from_year > to_year
    ):
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year.",
        )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # Verify company exists
        # ----------------------------------------------------

        company_exists = connection.execute(
            """
            SELECT 1
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        if company_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found.",
            )

        # ----------------------------------------------------
        # Build query
        # ----------------------------------------------------

        query = """
            SELECT
                company_id,
                year,
                operating_activity,
                investing_activity,
                financing_activity,
                net_cash_flow
            FROM cashflow
            WHERE company_id = ?
              AND year IS NOT NULL
        """

        params = [company_id]

        # ----------------------------------------------------
        # From-year filter
        # ----------------------------------------------------

        if from_year is not None:
            query += """
                AND year >= ?
            """

            params.append(from_year)

        # ----------------------------------------------------
        # To-year filter
        # ----------------------------------------------------

        if to_year is not None:
            query += """
                AND year <= ?
            """

            params.append(to_year)

        # ----------------------------------------------------
        # Sort newest → oldest
        # ----------------------------------------------------

        query += """
            ORDER BY year DESC
        """

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:
        connection.close()

    # --------------------------------------------------------
    # Convert rows to dictionaries
    # --------------------------------------------------------

    records = [
        dict(row)
        for row in rows
    ]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "company_id": company_id,
        "count": len(records),
        "from_year": from_year,
        "to_year": to_year,
        "data": records,
    }
# ============================================================
# GET COMPANY FINANCIAL RATIOS
# ============================================================

@router.get("/{company_id}/ratios")
def get_company_ratios(
    company_id: str,
    year: Optional[int] = Query(
        default=None,
        description="Return ratios for a single year.",
    ),
    from_year: Optional[int] = Query(
        default=None,
        description="Starting year for the annual ratio history.",
    ),
    to_year: Optional[int] = Query(
        default=None,
        description="Ending year for the annual ratio history.",
    ),
):
    """
    Return annual financial ratios for a company.
    """

    # --------------------------------------------------------
    # Validate year range
    # --------------------------------------------------------

    if (
        from_year is not None
        and to_year is not None
        and from_year > to_year
    ):
        raise HTTPException(
            status_code=400,
            detail="from_year cannot be greater than to_year.",
        )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # Verify company exists
        # ----------------------------------------------------

        company_exists = connection.execute(
            """
            SELECT 1
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        if company_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Company '{company_id}' not found.",
            )

        # ----------------------------------------------------
        # Build query
        # ----------------------------------------------------

        query = """
            SELECT
                company_id,
                year,
                period_type,
                period_months,

                net_profit_margin_pct,
                operating_profit_margin_pct,

                return_on_equity_pct,
                return_on_capital_employed_pct,
                return_on_assets_pct,

                debt_to_equity,
                high_leverage_flag,

                interest_coverage,
                icr_label,
                low_interest_coverage_flag,

                net_debt_cr,
                asset_turnover,

                revenue_cagr_3y_pct,
                revenue_cagr_3y_flag,
                revenue_cagr_5y_pct,
                revenue_cagr_5y_flag,
                revenue_cagr_10y_pct,
                revenue_cagr_10y_flag,

                pat_cagr_3y_pct,
                pat_cagr_3y_flag,
                pat_cagr_5y_pct,
                pat_cagr_5y_flag,
                pat_cagr_10y_pct,
                pat_cagr_10y_flag,

                eps_cagr_3y_pct,
                eps_cagr_3y_flag,
                eps_cagr_5y_pct,
                eps_cagr_5y_flag,
                eps_cagr_10y_pct,
                eps_cagr_10y_flag,

                free_cash_flow_cr,

                cfo_quality_score,
                cfo_quality_label,

                capex_cr,
                capex_intensity_pct,
                fcf_conversion_rate_pct,

                earnings_per_share,
                book_value_per_share,

                dividend_payout_ratio_pct,

                total_debt_cr,
                cash_from_operations_cr,

                composite_quality_score

            FROM financial_ratios

            WHERE company_id = ?
              AND period_type = 'ANNUAL'
              AND year IS NOT NULL
        """

        params = [company_id]

        # --------------------------------------------------------
        # Single-year filter
        # --------------------------------------------------------

        if year is not None:
            query += """
                AND year = ?
            """

            params.append(year)

        # --------------------------------------------------------
        # From-year filter
        # --------------------------------------------------------

        if from_year is not None:
            query += """
                AND year >= ?
            """

            params.append(from_year)

        # --------------------------------------------------------
        # To-year filter
        # --------------------------------------------------------

        if to_year is not None:
            query += """
                AND year <= ?
            """

            params.append(to_year)

        # ----------------------------------------------------
        # Sort newest → oldest
        # ----------------------------------------------------

        query += """
            ORDER BY year DESC
        """

        rows = connection.execute(
            query,
            params,
        ).fetchall()

    finally:
        connection.close()

    # --------------------------------------------------------
    # Convert rows to dictionaries
    # --------------------------------------------------------

    records = [
        dict(row)
        for row in rows
    ]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "company_id": company_id,
        "count": len(records),
        "year": year,
        "from_year": from_year,
        "to_year": to_year,
        "data": records,
    }
        
# ============================================================
# GET COMPANY TEARSHEET PDF
# ============================================================

@router.get("/{company_id}/tearsheet")
def get_company_tearsheet(company_id: str):
    """
    Return the pre-generated company tearsheet PDF.
    """

    # --------------------------------------------------------
    # Tearsheets directory
    # --------------------------------------------------------

    tearsheet_dir = (
        PROJECT_ROOT
        / "reports"
        / "tearsheets"
    )

    # --------------------------------------------------------
    # Find company tearsheet
    # --------------------------------------------------------

    pdf_path = None

    for path in tearsheet_dir.glob("*.pdf"):

        if path.stem.upper() == f"{company_id.upper()}_TEARSHEET":
            pdf_path = path
            break

    # --------------------------------------------------------
    # PDF not found
    # --------------------------------------------------------

    if pdf_path is None:

        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet PDF for company '{company_id}' not found.",
        )

    # --------------------------------------------------------
    # Return PDF
    # --------------------------------------------------------

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )