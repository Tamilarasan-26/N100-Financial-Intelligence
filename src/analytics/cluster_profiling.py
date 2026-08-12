from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
CLUSTER_FILE = PROJECT_ROOT / "output" / "cluster_labels.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD CLUSTER LABELS
# ============================================================

clusters = pd.read_csv(CLUSTER_FILE)

clusters["company_id"] = (
    clusters["company_id"]
    .astype(str)
    .str.strip()
)

print("=" * 60)
print("CLUSTER PROFILING")
print("=" * 60)

print("Cluster companies :", len(clusters))
print("Unique companies  :", clusters["company_id"].nunique())


# ============================================================
# VALIDATE CLUSTER FILE
# ============================================================

required_cluster_columns = [
    "company_id",
    "cluster_id",
    "cluster_name",
]

missing_columns = [
    col
    for col in required_cluster_columns
    if col not in clusters.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in cluster_labels.csv: {missing_columns}"
    )

if clusters["company_id"].duplicated().any():
    raise ValueError(
        "Duplicate company IDs found in cluster_labels.csv"
    )


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

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
)

ratios["year"] = ratios["year"].astype(int)


# ============================================================
# CALCULATE 5-YEAR FCF CAGR
#
# IMPORTANT:
# fcf_cagr_5yr DOES NOT EXIST IN THE DATABASE.
#
# It is calculated from:
# free_cash_flow_cr
# ============================================================

def calculate_fcf_cagr(group):

    group = group.sort_values("year")

    latest_year = group["year"].max()
    start_year = latest_year - 5

    latest_rows = group[
        group["year"] == latest_year
    ]

    start_rows = group[
        group["year"] == start_year
    ]

    if latest_rows.empty:
        return np.nan

    if start_rows.empty:
        return np.nan

    latest_fcf = latest_rows.iloc[-1]["free_cash_flow_cr"]
    start_fcf = start_rows.iloc[-1]["free_cash_flow_cr"]

    if pd.isna(latest_fcf):
        return np.nan

    if pd.isna(start_fcf):
        return np.nan

    if start_fcf <= 0:
        return np.nan

    if latest_fcf <= 0:
        return np.nan

    return (
        (latest_fcf / start_fcf) ** (1 / 5) - 1
    ) * 100


fcf_cagr = (
    ratios
    .groupby("company_id")
    .apply(
        calculate_fcf_cagr,
        include_groups=False,
    )
    .reset_index(
        name="fcf_cagr_5yr"
    )
)


# ============================================================
# SELECT LATEST YEAR
# ============================================================

latest = (
    ratios
    .sort_values(
        ["company_id", "year"]
    )
    .groupby(
        "company_id",
        as_index=False,
    )
    .tail(1)
    .copy()
)


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
# VERIFY FCF CAGR
# ============================================================

print()
print("Financial columns after FCF calculation:")
print(latest.columns.tolist())

print()
print(
    "FCF CAGR calculated for:",
    latest["fcf_cagr_5yr"].notna().sum(),
    "companies",
)

if "fcf_cagr_5yr" not in latest.columns:
    raise ValueError(
        "FCF CAGR column was not created."
    )


# ============================================================
# MERGE CLUSTER LABELS
# ============================================================

df = clusters.merge(
    latest,
    on="company_id",
    how="left",
    validate="one_to_one",
)


# ============================================================
# VALIDATION
# ============================================================

print()
print("Financial rows     :", len(latest))
print("Merged rows        :", len(df))
print(
    "Unique companies   :",
    df["company_id"].nunique(),
)


if len(latest) != 92:
    raise ValueError(
        f"Expected 92 financial companies, found {len(latest)}"
    )

if len(df) != 92:
    raise ValueError(
        f"Expected 92 merged rows, found {len(df)}"
    )

if df["company_id"].duplicated().any():
    raise ValueError(
        "Duplicate companies found after merge."
    )


# ============================================================
# CHECK FEATURES
# ============================================================

missing_features = (
    df[FEATURES]
    .isna()
    .sum()
)

print()
print("Missing values:")
print(
    missing_features.to_string()
)


# ============================================================
# CHECK CLUSTER ASSIGNMENTS
# ============================================================

if df["cluster_id"].isna().any():
    raise ValueError(
        "Missing cluster IDs detected."
    )

if df["cluster_name"].isna().any():
    raise ValueError(
        "Missing cluster names detected."
    )


# ============================================================
# CREATE CLUSTER PROFILES
# ============================================================

profile_rows = []

for cluster_id in sorted(
    df["cluster_id"].unique()
):

    subset = df[
        df["cluster_id"] == cluster_id
    ]

    cluster_name = subset[
        "cluster_name"
    ].iloc[0]

    row = {
        "cluster_id": int(cluster_id),
        "cluster_name": cluster_name,
        "companies": len(subset),
    }

    for feature in FEATURES:

        row[
            f"{feature}_mean"
        ] = subset[feature].mean()

        row[
            f"{feature}_median"
        ] = subset[feature].median()

    profile_rows.append(row)


# ============================================================
# CREATE PROFILE DATAFRAME
# ============================================================

profile = pd.DataFrame(
    profile_rows
)


# ============================================================
# ROUND VALUES
# ============================================================

numeric_columns = (
    profile
    .select_dtypes(
        include="number"
    )
    .columns
)

profile[numeric_columns] = (
    profile[numeric_columns]
    .round(2)
)


# ============================================================
# SAVE OUTPUT
# ============================================================

output_file = (
    OUTPUT_DIR / "cluster_profiles.csv"
)

profile.to_csv(
    output_file,
    index=False,
)


# ============================================================
# DISPLAY CLUSTER PROFILES
# ============================================================

print()
print("Cluster Profiles:")
print(
    profile.to_string(
        index=False
    )
)


# ============================================================
# CLUSTER DISTRIBUTION
# ============================================================

print()
print("Cluster distribution:")

distribution = (
    df
    .groupby(
        [
            "cluster_id",
            "cluster_name",
        ]
    )
    .size()
    .reset_index(
        name="companies"
    )
)

print(
    distribution.to_string(
        index=False
    )
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("Final validation:")

print(
    "Rows               :",
    len(df),
)

print(
    "Unique companies   :",
    df["company_id"].nunique(),
)

print(
    "Unique clusters    :",
    df["cluster_id"].nunique(),
)

print(
    "Duplicate companies:",
    df["company_id"].duplicated().sum(),
)

print(
    "Missing cluster IDs:",
    df["cluster_id"].isna().sum(),
)

print(
    "Missing names      :",
    df["cluster_name"].isna().sum(),
)


# ============================================================
# FINISH
# ============================================================

print()
print("Output saved:")
print(output_file)

print()
print("Day 37 — Cluster profiling complete.")
