from fastapi import APIRouter, HTTPException
import sqlite3
from statistics import median

from src.api.main import DB_PATH


router = APIRouter()


# ============================================================
# GET ALL SECTORS
# ============================================================

@router.get("/sectors")
def get_sectors():
    """
    Return all sectors with company count and median financial metrics.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # Get latest financial ratios
        # ----------------------------------------------------

        query = """
        WITH latest_ratios AS (
            SELECT
                fr.company_id,
                fr.return_on_equity_pct AS roe,
                fr.debt_to_equity AS debt_to_equity
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
        ),

        latest_market_cap AS (
            SELECT
                mc.company_id,
                mc.pe_ratio
            FROM market_cap mc

            INNER JOIN (
                SELECT
                    company_id,
                    MAX(year) AS latest_year
                FROM market_cap
                GROUP BY company_id
            ) latest

                ON mc.company_id = latest.company_id
                AND mc.year = latest.latest_year
        )

        SELECT
            c.broad_sector AS sector,
            c.id AS company_id,
            lr.roe,
            lr.debt_to_equity,
            lmc.pe_ratio

        FROM companies c

        LEFT JOIN latest_ratios lr
            ON c.id = lr.company_id

        LEFT JOIN latest_market_cap lmc
            ON c.id = lmc.company_id

        WHERE c.broad_sector IS NOT NULL

        ORDER BY c.broad_sector
        """

        rows = connection.execute(query).fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No sector data found."
            )

        # ----------------------------------------------------
        # Group companies by sector
        # ----------------------------------------------------

        sector_data = {}

        for row in rows:

            sector = row["sector"]

            if sector not in sector_data:
                sector_data[sector] = {
                    "roe": [],
                    "pe": [],
                    "de": [],
                }

            if row["roe"] is not None:
                sector_data[sector]["roe"].append(
                    row["roe"]
                )

            if row["pe_ratio"] is not None:
                sector_data[sector]["pe"].append(
                    row["pe_ratio"]
                )

            if row["debt_to_equity"] is not None:
                sector_data[sector]["de"].append(
                    row["debt_to_equity"]
                )

        # ----------------------------------------------------
        # Calculate sector statistics
        # ----------------------------------------------------

        sectors = []

        for sector, values in sector_data.items():

            company_count = sum(
                1
                for row in rows
                if row["sector"] == sector
            )

            sectors.append({
                "sector": sector,

                "company_count": company_count,

                "median_roe": (
                    round(median(values["roe"]), 2)
                    if values["roe"]
                    else None
                ),

                "median_pe": (
                    round(median(values["pe"]), 2)
                    if values["pe"]
                    else None
                ),

                "median_de": (
                    round(median(values["de"]), 2)
                    if values["de"]
                    else None
                ),
            })

        # ----------------------------------------------------
        # Sort sectors alphabetically
        # ----------------------------------------------------

        sectors.sort(
            key=lambda x: x["sector"]
        )

        return {
            "count": len(sectors),
            "sectors": sectors,
        }

    finally:

        connection.close()


# ============================================================
# GET COMPANIES BY SECTOR
# ============================================================

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    """
    Return all companies in a sector with latest-year KPIs.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. CHECK WHETHER SECTOR EXISTS
        # ----------------------------------------------------

        sector_row = connection.execute(
            """
            SELECT 1
            FROM companies
            WHERE broad_sector = ?
            LIMIT 1
            """,
            (sector,),
        ).fetchone()

        if sector_row is None:

            raise HTTPException(
                status_code=404,
                detail=f"Sector '{sector}' not found.",
            )

        # ----------------------------------------------------
        # 2. GET LATEST FINANCIAL RATIOS
        # ----------------------------------------------------

        query = """
        WITH latest_ratios AS (

            SELECT
                fr.company_id,
                fr.year,

                fr.return_on_equity_pct AS roe_pct,

                fr.debt_to_equity,

                fr.revenue_cagr_5y_pct,

                fr.pat_cagr_5y_pct,

                fr.free_cash_flow_cr,

                fr.composite_quality_score

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

            c.id,

            c.company_name,

            c.broad_sector,

            c.sub_sector,

            c.market_cap_category,

            lr.year,

            lr.roe_pct,

            lr.debt_to_equity,

            lr.revenue_cagr_5y_pct,

            lr.pat_cagr_5y_pct,

            lr.free_cash_flow_cr,

            lr.composite_quality_score

        FROM companies c

        LEFT JOIN latest_ratios lr

            ON c.id = lr.company_id

        WHERE c.broad_sector = ?

        ORDER BY c.company_name
        """

        rows = connection.execute(
            query,
            (sector,),
        ).fetchall()

        # ----------------------------------------------------
        # 3. BUILD COMPANY RESPONSE
        # ----------------------------------------------------

        companies = []

        for row in rows:

            companies.append({

                "id": row["id"],

                "company_name": row["company_name"],

                "broad_sector": row["broad_sector"],

                "sub_sector": row["sub_sector"],

                "market_cap_category":
                    row["market_cap_category"],

                "year": row["year"],

                "roe_pct": row["roe_pct"],

                "debt_to_equity":
                    row["debt_to_equity"],

                "revenue_cagr_5y_pct":
                    row["revenue_cagr_5y_pct"],

                "pat_cagr_5y_pct":
                    row["pat_cagr_5y_pct"],

                "free_cash_flow_cr":
                    row["free_cash_flow_cr"],

                "composite_quality_score":
                    row["composite_quality_score"],
            })

        # ----------------------------------------------------
        # 4. RETURN RESPONSE
        # ----------------------------------------------------

        return {

            "sector": sector,

            "count": len(companies),

            "companies": companies,

        }

    finally:

        connection.close()