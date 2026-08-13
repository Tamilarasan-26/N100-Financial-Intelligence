from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# KPI DEFINITIONS
# ============================================================

KPI_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "pat_cagr_5y_pct",
    "operating_profit_margin_pct",
    "interest_coverage",
    "free_cash_flow_cr",
    "asset_turnover",
    "pe_ratio",
    "pb_ratio",
]


KPI_LABELS = {
    "return_on_equity_pct": "ROE",
    "debt_to_equity": "Debt / Equity",
    "revenue_cagr_5y_pct": "Revenue CAGR 5Y",
    "pat_cagr_5y_pct": "PAT CAGR 5Y",
    "operating_profit_margin_pct": "Operating Margin",
    "interest_coverage": "Interest Coverage",
    "free_cash_flow_cr": "Free Cash Flow",
    "asset_turnover": "Asset Turnover",
    "pe_ratio": "P/E",
    "pb_ratio": "P/B",
}


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("PORTFOLIO STATISTICS")
print("=" * 60)


# ============================================================
# DATABASE CONNECTION
# ============================================================

con = sqlite3.connect(DB_PATH)


# ============================================================
# LOAD COMPANIES
# ============================================================

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        company_name,
        broad_sector
    FROM companies
    ORDER BY id
    """,
    con,
)


# ============================================================
# LOAD LATEST ANNUAL FINANCIAL RATIOS
# ============================================================

financials = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        return_on_equity_pct,
        debt_to_equity,
        revenue_cagr_5y_pct,
        pat_cagr_5y_pct,
        operating_profit_margin_pct,
        interest_coverage,
        free_cash_flow_cr,
        asset_turnover
    FROM financial_ratios
    WHERE period_type = 'ANNUAL'
    ORDER BY company_id, year
    """,
    con,
)


# ============================================================
# LOAD LATEST MARKET CAP / VALUATION DATA
# ============================================================

market_cap = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        pe_ratio,
        pb_ratio
    FROM market_cap
    ORDER BY company_id, year
    """,
    con,
)


con.close()


# ============================================================
# NORMALIZE COMPANY IDs
# ============================================================

companies["company_id"] = companies["company_id"].astype(str)

financials["company_id"] = financials["company_id"].astype(str)

market_cap["company_id"] = market_cap["company_id"].astype(str)


# ============================================================
# NORMALIZE YEARS
# ============================================================

financials["year"] = pd.to_numeric(
    financials["year"],
    errors="coerce",
)

financials = financials.dropna(subset=["year"])

financials["year"] = financials["year"].astype(int)


market_cap["year"] = pd.to_numeric(
    market_cap["year"],
    errors="coerce",
)

market_cap = market_cap.dropna(subset=["year"])

market_cap["year"] = market_cap["year"].astype(int)


# ============================================================
# SELECT LATEST ANNUAL FINANCIAL RECORD
# ============================================================

financials = (
    financials
    .sort_values(["company_id", "year"])
    .drop_duplicates(
        subset=["company_id"],
        keep="last",
    )
    .copy()
)


# ============================================================
# SELECT LATEST MARKET CAP RECORD
# ============================================================

market_cap = (
    market_cap
    .sort_values(["company_id", "year"])
    .drop_duplicates(
        subset=["company_id"],
        keep="last",
    )
    .copy()
)


# ============================================================
# MERGE FINANCIAL + VALUATION DATA
# ============================================================

df = companies.merge(
    financials,
    on="company_id",
    how="left",
    validate="one_to_one",
)

df = df.merge(
    market_cap,
    on="company_id",
    how="left",
    suffixes=("", "_market"),
    validate="one_to_one",
)


# ============================================================
# VALIDATION — COMPANY UNIVERSE
# ============================================================

print(f"Companies loaded : {len(companies)}")
print(f"Financial rows   : {len(financials)}")
print(f"Market-cap rows  : {len(market_cap)}")
print(f"Final rows       : {len(df)}")
print(
    f"Unique companies : "
    f"{df['company_id'].nunique()}"
)


if len(df) != 92:
    raise ValueError(
        f"Expected 92 companies, found {len(df)}"
    )


if df["company_id"].nunique() != 92:
    raise ValueError(
        "Duplicate or missing company IDs detected."
    )


# ============================================================
# CONVERT KPI COLUMNS TO NUMERIC
# ============================================================

for column in KPI_COLUMNS:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# MISSING VALUES
# ============================================================

print("\nMissing KPI values:")

missing_values = (
    df[KPI_COLUMNS]
    .isna()
    .sum()
)

print(
    missing_values.to_string()
)


# ============================================================
# CALCULATE PORTFOLIO STATISTICS
# ============================================================

stats_rows = []


for column in KPI_COLUMNS:

    series = df[column].dropna()

    if series.empty:
        raise ValueError(
            f"No valid values found for KPI: {column}"
        )

    row = {
        "kpi": KPI_LABELS[column],
        "source_column": column,
        "valid_companies": int(series.count()),
        "missing_companies": int(
            df[column].isna().sum()
        ),
        "P10": series.quantile(0.10),
        "P25": series.quantile(0.25),
        "P50": series.quantile(0.50),
        "P75": series.quantile(0.75),
        "P90": series.quantile(0.90),
        "Mean": series.mean(),
        "Std": series.std(),
    }

    stats_rows.append(row)


# ============================================================
# CREATE OUTPUT DATAFRAME
# ============================================================

stats = pd.DataFrame(stats_rows)


# ============================================================
# ROUND VALUES
# ============================================================

numeric_columns = [
    "P10",
    "P25",
    "P50",
    "P75",
    "P90",
    "Mean",
    "Std",
]


stats[numeric_columns] = (
    stats[numeric_columns]
    .round(2)
)


# ============================================================
# SAVE OUTPUT
# ============================================================

output_file = (
    OUTPUT_DIR / "portfolio_stats.csv"
)

stats.to_csv(
    output_file,
    index=False,
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PORTFOLIO STATISTICS")
print("=" * 60)

print(
    stats.to_string(index=False)
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("FINAL VALIDATION")
print("=" * 60)

print(
    f"Companies analyzed : "
    f"{df['company_id'].nunique()}"
)

print(
    f"KPIs analyzed      : "
    f"{len(stats)}"
)

print(
    f"Statistics columns : "
    f"{len(stats.columns)}"
)

print(
    f"Output rows        : "
    f"{len(stats)}"
)


if df["company_id"].nunique() != 92:
    raise ValueError(
        "Portfolio must contain exactly 92 companies."
    )


if len(stats) != 10:
    raise ValueError(
        f"Expected 10 KPIs, found {len(stats)}"
    )


required_statistics = [
    "P10",
    "P25",
    "P50",
    "P75",
    "P90",
    "Mean",
    "Std",
]


missing_statistics = [
    column
    for column in required_statistics
    if column not in stats.columns
]


if missing_statistics:
    raise ValueError(
        f"Missing statistics columns: "
        f"{missing_statistics}"
    )


print("\nOutput saved:")
print(output_file)

print("\nDay 37 — Portfolio statistics complete.")
