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

OUTPUT_FILE = OUTPUT_DIR / "outlier_report.csv"


# ============================================================
# FEATURES
# Same 5 features used for K-Means clustering
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

print("=" * 60)
print("OUTLIER DETECTION")
print("=" * 60)

con = sqlite3.connect(DB_PATH)

ratios = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        period_type,
        return_on_equity_pct,
        debt_to_equity,
        revenue_cagr_5y_pct,
        operating_profit_margin_pct,
        free_cash_flow_cr
    FROM financial_ratios
    WHERE period_type = 'ANNUAL'
    ORDER BY company_id, year
    """,
    con,
)

con.close()


# ============================================================
# NORMALIZE TYPES
# ============================================================

ratios["company_id"] = (
    ratios["company_id"]
    .astype(str)
    .str.strip()
)

ratios["year"] = pd.to_numeric(
    ratios["year"],
    errors="coerce",
)

ratios = ratios.dropna(
    subset=["year"]
).copy()

ratios["year"] = ratios["year"].astype(int)


# ============================================================
# CALCULATE 5-YEAR FCF CAGR
# Same calculation used in clustering.py
# ============================================================

def calculate_fcf_cagr(group):
    """
    Calculate five-year FCF CAGR using the latest
    available annual year and the year five years earlier.
    """

    group = group.sort_values("year").copy()

    latest_year = group["year"].max()
    start_year = latest_year - 5

    latest_rows = group[
        group["year"] == latest_year
    ]

    start_rows = group[
        group["year"] == start_year
    ]

    if latest_rows.empty or start_rows.empty:
        return np.nan

    latest_fcf = latest_rows.iloc[-1]["free_cash_flow_cr"]
    start_fcf = start_rows.iloc[-1]["free_cash_flow_cr"]

    if pd.isna(latest_fcf) or pd.isna(start_fcf):
        return np.nan

    if start_fcf <= 0 or latest_fcf <= 0:
        return np.nan

    return (
        (latest_fcf / start_fcf) ** (1 / 5) - 1
    ) * 100


fcf_cagr = (
    ratios
    .groupby("company_id")
    .apply(calculate_fcf_cagr)
    .reset_index(name="fcf_cagr_5yr")
)


# ============================================================
# SELECT LATEST ANNUAL RECORD
# ============================================================

latest = (
    ratios
    .sort_values(["company_id", "year"])
    .groupby("company_id", as_index=False)
    .tail(1)
    .copy()
)


# ============================================================
# KEEP REQUIRED COLUMNS
# ============================================================

latest = latest[
    [
        "company_id",
        "year",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5y_pct",
        "operating_profit_margin_pct",
    ]
]


# ============================================================
# ADD FCF CAGR
# ============================================================

latest = latest.merge(
    fcf_cagr,
    on="company_id",
    how="left",
    validate="one_to_one",
)


# ============================================================
# LOAD COMPANY SECTOR
# ============================================================

con = sqlite3.connect(DB_PATH)

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        company_name,
        broad_sector,
        sub_sector
    FROM companies
    """,
    con,
)

con.close()


# ============================================================
# NORMALIZE COMPANY IDS
# ============================================================

companies["company_id"] = (
    companies["company_id"]
    .astype(str)
    .str.strip()
)


# ============================================================
# MERGE SECTOR INFORMATION
# ============================================================

df = latest.merge(
    companies,
    on="company_id",
    how="left",
    validate="one_to_one",
)


# ============================================================
# VALIDATION
# ============================================================

print(
    f"Companies loaded : {df['company_id'].nunique()}"
)

print(
    f"Latest rows      : {len(df)}"
)

print(
    f"Missing sectors  : {df['broad_sector'].isna().sum()}"
)


if df["company_id"].nunique() != 92:
    raise ValueError(
        f"Expected 92 companies, found "
        f"{df['company_id'].nunique()}"
    )

if len(df) != 92:
    raise ValueError(
        f"Expected 92 rows, found {len(df)}"
    )


# ============================================================
# MISSING VALUE CHECK
# ============================================================

print("\nMissing feature values:")

print(
    df[FEATURES]
    .isna()
    .sum()
    .to_string()
)


# ============================================================
# CALCULATE SECTOR-LEVEL Z-SCORES
#
# Z = (company value - sector mean) / sector std
#
# Outlier threshold:
# absolute Z-score > 3
# ============================================================

print("\nCalculating sector-level Z-scores...")


zscore_columns = []


for feature in FEATURES:

    zscore_column = f"{feature}_zscore"

    sector_mean = (
        df.groupby("broad_sector")[feature]
        .transform("mean")
    )

    sector_std = (
        df.groupby("broad_sector")[feature]
        .transform("std")
    )

    df[zscore_column] = (
        (df[feature] - sector_mean)
        / sector_std.replace(0, np.nan)
    )

    zscore_columns.append(zscore_column)


# ============================================================
# OUTLIER FLAGS
# ============================================================

flag_columns = []


for feature in FEATURES:

    zscore_column = f"{feature}_zscore"
    flag_column = f"{feature}_outlier"

    df[flag_column] = (
        df[zscore_column]
        .abs()
        > 3
    )

    flag_columns.append(flag_column)


# ============================================================
# ANY OUTLIER
# ============================================================

df["any_outlier"] = df[
    flag_columns
].any(axis=1)


# ============================================================
# LIST OUTLIER METRICS
# ============================================================

def get_outlier_metrics(row):
    metrics = []

    for feature in FEATURES:

        flag_column = f"{feature}_outlier"

        if bool(row[flag_column]):
            metrics.append(feature)

    return ", ".join(metrics)


df["outlier_metrics"] = df.apply(
    get_outlier_metrics,
    axis=1,
)


# ============================================================
# MAXIMUM ABSOLUTE Z-SCORE
# ============================================================

df["max_abs_zscore"] = (
    df[zscore_columns]
    .abs()
    .max(axis=1)
)


# ============================================================
# CREATE FINAL OUTLIER REPORT
# Only companies with at least one |Z| > 3
# ============================================================

outliers = df[
    df["any_outlier"]
].copy()


# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [
    "company_id",
    "company_name",
    "broad_sector",
    "sub_sector",
    "year",
    "outlier_metrics",
    "max_abs_zscore",
]


# Add feature values and Z-scores
for feature in FEATURES:

    output_columns.append(feature)
    output_columns.append(
        f"{feature}_zscore"
    )


outlier_report = outliers[
    output_columns
].copy()


# ============================================================
# ROUND NUMERIC VALUES
# ============================================================

numeric_columns = (
    outlier_report
    .select_dtypes(include="number")
    .columns
)

outlier_report[numeric_columns] = (
    outlier_report[numeric_columns]
    .round(2)
)


# ============================================================
# SORT
# ============================================================

outlier_report = (
    outlier_report
    .sort_values(
        "max_abs_zscore",
        ascending=False,
    )
    .reset_index(drop=True)
)


# ============================================================
# SAVE
# ============================================================

outlier_report.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("OUTLIER RESULTS")
print("=" * 60)

print(
    f"Total companies       : {len(df)}"
)

print(
    f"Companies with outlier: {len(outlier_report)}"
)

print(
    f"Threshold             : |Z-score| > 3"
)


print("\nOutlier report:")

if outlier_report.empty:

    print(
        "No companies exceeded the "
        "|Z-score| > 3 threshold."
    )

else:

    print(
        outlier_report[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "outlier_metrics",
                "max_abs_zscore",
            ]
        ].to_string(index=False)
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\nFinal validation:")

print(
    f"Input companies       : {df['company_id'].nunique()}"
)

print(
    f"Input rows             : {len(df)}"
)

print(
    f"Outlier companies      : {len(outlier_report)}"
)

print(
    f"Output columns         : {len(outlier_report.columns)}"
)

print(
    f"Output saved           : {OUTPUT_FILE}"
)


if not OUTPUT_FILE.exists():
    raise FileNotFoundError(
        "outlier_report.csv was not created."
    )


print(
    "\nDay 37 — Outlier detection complete."
)