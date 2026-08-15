from fastapi import APIRouter, HTTPException
import sqlite3
from urllib.parse import urlparse

from src.api.main import DB_PATH


router = APIRouter()


# ============================================================
# URL VALIDATION
# ============================================================

def is_valid_url(url):
    """
    Check whether a value is a valid HTTP or HTTPS URL.
    """

    if not url:
        return False

    try:
        parsed = urlparse(url)

        return parsed.scheme in ("http", "https") and bool(
            parsed.netloc
        )

    except Exception:
        return False


# ============================================================
# GET COMPANY DOCUMENTS
# ============================================================

@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    """
    Return annual report links for a company with URL validity flags.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. CHECK WHETHER COMPANY EXISTS
        # ----------------------------------------------------

        company = connection.execute(
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

        if company is None:

            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        # ----------------------------------------------------
        # 2. GET ANNUAL REPORT DOCUMENTS
        # ----------------------------------------------------

        rows = connection.execute(
            """
            SELECT
                year,
                annual_report
            FROM documents
            WHERE company_id = ?
            ORDER BY year
            """,
            (ticker.upper(),),
        ).fetchall()

        # ----------------------------------------------------
        # 3. BUILD DOCUMENT RESPONSE
        # ----------------------------------------------------

        documents = []

        for row in rows:

            annual_report = row["annual_report"]

            documents.append({
                "year": row["year"],
                "annual_report": annual_report,
                "is_url_valid": is_valid_url(
                    annual_report
                ),
            })

        # ----------------------------------------------------
        # 4. RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "company_id": company["id"],
            "company_name": company["company_name"],
            "count": len(documents),
            "documents": documents,
        }

    finally:

        connection.close()