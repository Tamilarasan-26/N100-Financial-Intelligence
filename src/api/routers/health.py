from pathlib import Path
import sqlite3
import time

from fastapi import APIRouter


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_VERSION = "1.0.0"

START_TIME = time.time()


# ============================================================
# DATABASE TABLES
# ============================================================

DATABASE_TABLES = [
    "balancesheet",
    "capital_allocation",
    "cashflow",
    "companies",
    "company_insights",
    "documents",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "peer_percentiles",
    "profitandloss",
    "stock_prices",
]


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@router.get("")
def health_check():
    """
    Return API and database health information.
    """

    db_row_counts = {}

    connection = sqlite3.connect(DB_PATH)

    try:

        for table in DATABASE_TABLES:

            query = (
                f'SELECT COUNT(*) AS count '
                f'FROM "{table}"'
            )

            result = connection.execute(
                query
            ).fetchone()

            db_row_counts[table] = result[0]

    finally:

        connection.close()

    uptime_seconds = (
        time.time() - START_TIME
    )

    return {
        "status": "ok",
        "db_row_counts": db_row_counts,
        "uptime_seconds": round(
            uptime_seconds,
            2,
        ),
        "version": APP_VERSION,
    }