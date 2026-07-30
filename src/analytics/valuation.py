import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------
# Connect to Database
# ---------------------------------------------

con = sqlite3.connect(DB_PATH)

# ---------------------------------------------
# Load Companies
# ---------------------------------------------

companies = pd.read_sql("""
SELECT
    id,
    company_name,
    broad_sector
FROM companies
""", con)

# ---------------------------------------------
# Load Market Cap Data
# ---------------------------------------------

market = pd.read_sql("""
SELECT
    company_id,
    year,
    market_cap_crore,
    pe_ratio,
    pb_ratio,
    ev_ebitda
FROM market_cap
""", con)

# ---------------------------------------------
# Load Financial Ratios
# ---------------------------------------------

ratios = pd.read_sql("""
SELECT
    company_id,
    year,
    free_cash_flow_cr
FROM financial_ratios
""", con)

# ---------------------------------------------
# Merge All Tables
# ---------------------------------------------

valuation_df = companies.merge(
    market,
    left_on="id",
    right_on="company_id",
    how="inner"
)

valuation_df = valuation_df.merge(
    ratios,
    on=["company_id", "year"],
    how="inner"
)

print("Merged Data")
print(valuation_df.head())

# ---------------------------------------------
# Calculate FCF Yield
# ---------------------------------------------

valuation_df["fcf_yield_pct"] = (
    valuation_df["free_cash_flow_cr"] /
    valuation_df["market_cap_crore"]
) * 100

print("\nFCF Yield")
print(
    valuation_df[
        [
            "company_name",
            "year",
            "market_cap_crore",
            "free_cash_flow_cr",
            "fcf_yield_pct"
        ]
    ].head()
)

# ---------------------------------------------
# Calculate Sector Median P/E
# ---------------------------------------------

sector_pe = (
    valuation_df
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_pe.rename(
    columns={"pe_ratio": "sector_median_pe"},
    inplace=True
)

print("\nSector Median P/E")
print(sector_pe.head())

# ---------------------------------------------
# Merge Sector Median P/E
# ---------------------------------------------

valuation_df = valuation_df.merge(
    sector_pe,
    on="broad_sector",
    how="left"
)

# ---------------------------------------------
# Assign Valuation Flag
# ---------------------------------------------

def valuation_flag(row):

    if row["pe_ratio"] < row["sector_median_pe"] * 0.7:
        return "Discount"

    elif row["pe_ratio"] > row["sector_median_pe"] * 1.5:
        return "Caution"

    else:
        return "Fair"

valuation_df["valuation_flag"] = valuation_df.apply(
    valuation_flag,
    axis=1
)

print("\nValuation Summary")
print(
    valuation_df[
        [
            "company_name",
            "year",
            "broad_sector",
            "pe_ratio",
            "sector_median_pe",
            "valuation_flag"
        ]
    ].head(10)
)

# ---------------------------------------------
# Export Valuation Summary
# ---------------------------------------------

summary_columns = [
    "company_name",
    "year",
    "broad_sector",
    "market_cap_crore",
    "free_cash_flow_cr",
    "fcf_yield_pct",
    "pe_ratio",
    "sector_median_pe",
    "valuation_flag"
]

valuation_summary = valuation_df[summary_columns]

# Save Excel
valuation_summary.to_excel(
    OUTPUT_DIR / "valuation_summary.xlsx",
    index=False
)

# Save CSV
valuation_summary.to_csv(
    OUTPUT_DIR / "valuation_flags.csv",
    index=False
)

print("\n✅ Files Generated Successfully!")
print(f"Excel : {OUTPUT_DIR / 'valuation_summary.xlsx'}")
print(f"CSV   : {OUTPUT_DIR / 'valuation_flags.csv'}")