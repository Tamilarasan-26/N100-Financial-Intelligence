from pathlib import Path
import sqlite3
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_VERSION = "1.0.0"

START_TIME = time.time()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="N100 Financial Intelligence API",
    description="API for Nifty 100 financial intelligence analytics.",
    version=APP_VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed_time = (
        time.perf_counter() - start_time
    ) * 1000

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"{response.status_code} "
        f"{elapsed_time:.2f} ms"
    )

    return response


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    """
    Create a SQLite database connection.
    """

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


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
# HEALTH ENDPOINT
# ============================================================

@app.get(
    "/api/v1/health",
    tags=["Health"],
)
def health_check():
    """
    Return API and database health information.
    """

    db_row_counts = {}

    connection = get_db_connection()

    try:

        for table in DATABASE_TABLES:

            query = (
                f'SELECT COUNT(*) AS count '
                f'FROM "{table}"'
            )

            result = connection.execute(
                query
            ).fetchone()

            db_row_counts[table] = result["count"]

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


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["Health"],
)
def root():
    return {
        "name": "N100 Financial Intelligence API",
        "version": APP_VERSION,
        "status": "running",
    }


# ============================================================
# ROUTER IMPORTS
# ============================================================

from src.api.routers import (
    companies,
    screener,
    sectors,
    peers,
    valuation,
    portfolio,
    documents,
    health,
)


# ============================================================
# ROUTER REGISTRATION
# ============================================================

app.include_router(
    companies.router,
    prefix="/api/v1",
)

app.include_router(
    screener.router,
    prefix="/api/v1",
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
)

app.include_router(
    peers.router,
    prefix="/api/v1",
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    health.router,
    prefix="/api/v1",
)


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE API")
    print("=" * 60)
    print(f"Database : {DB_PATH}")
    print(f"Version  : {APP_VERSION}")
    print("API ready.")