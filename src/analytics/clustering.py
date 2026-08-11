from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORT_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
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
    con
)

companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        broad_sector
    FROM companies
    """,
    con
)

con.close()


# ============================================================
# NORMALIZE TYPES
# ============================================================

ratios["year"] = pd.to_numeric(
    ratios["year"],
    errors="coerce"
)

ratios = ratios.dropna(subset=["year"])
ratios["year"] = ratios["year"].astype(int)

companies["company_id"] = companies["company_id"].astype(str)
ratios["company_id"] = ratios["company_id"].astype(str)


# ============================================================
# CALCULATE 5-YEAR FCF CAGR
# ============================================================

def calculate_fcf_cagr(group):
    """
    Calculate 5-year FCF CAGR when both endpoint FCF values
    are positive. Negative or zero starting FCF produces NaN.
    """

    group = group.sort_values("year").copy()

    latest_year = group["year"].max()
    start_year = latest_year - 5

    latest_rows = group[group["year"] == latest_year]
    start_rows = group[group["year"] == start_year]

    if latest_rows.empty or start_rows.empty:
        return np.nan

    latest_fcf = latest_rows.iloc[-1]["free_cash_flow_cr"]
    start_fcf = start_rows.iloc[-1]["free_cash_flow_cr"]

    if pd.isna(latest_fcf) or pd.isna(start_fcf):
        return np.nan

    if start_fcf <= 0 or latest_fcf <= 0:
        return np.nan

    return ((latest_fcf / start_fcf) ** (1 / 5) - 1) * 100


fcf_cagr = (
    ratios.groupby("company_id")
    .apply(calculate_fcf_cagr)
    .reset_index(name="fcf_cagr_5yr")
)


# ============================================================
# SELECT LATEST YEAR
# ============================================================

latest = (
    ratios.sort_values(["company_id", "year"])
    .groupby("company_id", as_index=False)
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
        "operating_profit_margin_pct"
    ]
]

latest = latest.merge(
    fcf_cagr,
    on="company_id",
    how="left"
)

latest = latest.merge(
    companies,
    on="company_id",
    how="left"
)


# ============================================================
# FEATURE DEFINITIONS
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]


# ============================================================
# VALIDATE COMPANY UNIVERSE
# ============================================================

print("=" * 60)
print("K-MEANS CLUSTERING")
print("=" * 60)

print(f"Companies loaded : {latest['company_id'].nunique()}")
print(f"Rows loaded      : {len(latest)}")

if latest["company_id"].nunique() != 92:
    raise ValueError(
        f"Expected 92 companies, found "
        f"{latest['company_id'].nunique()}"
    )


# ============================================================
# SECTOR-MEDIAN IMPUTATION
# ============================================================

print("\nMissing values before imputation:")

print(
    latest[FEATURES]
    .isna()
    .sum()
    .to_string()
)


for feature in FEATURES:

    sector_median = latest.groupby("broad_sector")[feature].transform(
        "median"
    )

    latest[feature] = latest[feature].fillna(sector_median)

    # Final fallback in case an entire sector is missing
    latest[feature] = latest[feature].fillna(
        latest[feature].median()
    )


print("\nMissing values after imputation:")

print(
    latest[FEATURES]
    .isna()
    .sum()
    .to_string()
)


if latest[FEATURES].isna().any().any():
    raise ValueError("Missing values remain after imputation.")


# ============================================================
# FEATURE MATRIX
# ============================================================

X = latest[FEATURES].copy()


# ------------------------------------------------------------
# ROBUST OUTLIER HANDLING
# ------------------------------------------------------------

print("\nApplying robust outlier treatment...")

for col in FEATURES:

    if col == "return_on_equity_pct":
        # ROE contains extreme accounting-driven outliers.
        lower = X[col].quantile(0.05)
        upper = X[col].quantile(0.95)
    else:
        lower = X[col].quantile(0.01)
        upper = X[col].quantile(0.99)

    X[col] = X[col].clip(
        lower=lower,
        upper=upper
    )

    print(
        f"{col}: "
        f"clipped to [{lower:.2f}, {upper:.2f}]"
    )


# ============================================================
# STANDARD SCALING
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# ELBOW ANALYSIS K = 2 TO 10
# ============================================================

inertias = []
k_values = range(2, 11)

for k in k_values:

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    model.fit(X_scaled)

    inertias.append(model.inertia_)


plt.figure(figsize=(9, 6))

plt.plot(
    list(k_values),
    inertias,
    marker="o"
)

plt.xlabel("Number of Clusters (K)")
plt.ylabel("Inertia")
plt.title("K-Means Elbow Plot")

plt.xticks(list(k_values))
plt.grid(True, alpha=0.3)

plt.tight_layout()

elbow_path = REPORT_DIR / "elbow_plot.png"

plt.savefig(
    elbow_path,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(f"\nElbow plot saved: {elbow_path}")


# ============================================================
# FINAL K-MEANS MODEL
# ============================================================

K = 5

kmeans = KMeans(
    n_clusters=K,
    random_state=42,
    n_init=20
)

cluster_ids = kmeans.fit_predict(X_scaled)

latest["cluster_id"] = cluster_ids


# ============================================================
# DISTANCE FROM CENTROID
# ============================================================

distances = np.linalg.norm(
    X_scaled - kmeans.cluster_centers_[cluster_ids],
    axis=1
)

latest["distance_from_centroid"] = distances


# ============================================================
# CLUSTER PROFILE
# ============================================================

profile = (
    latest
    .groupby("cluster_id")[FEATURES]
    .mean()
)

print("\nCluster profiles:")
print(profile.round(2).to_string())


# ============================================================
# DESCRIPTIVE CLUSTER NAMES
# ============================================================

cluster_names = {
    0: "Low-Growth / Recovery",
    1: "High-Quality Compounders",
    2: "Exceptional ROE / Quality",
    3: "Leveraged / Cyclical",
    4: "Cash-Flow Compounders",
}

# Ensure every cluster has a descriptive name
latest["cluster_name"] = latest["cluster_id"].map(cluster_names)


# Ensure every cluster has a name
latest["cluster_name"] = latest["cluster_id"].map(
    cluster_names
)


# ============================================================
# SAVE OUTPUT
# ============================================================

output = latest[
    [
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid"
    ]
].copy()

output = output.sort_values(
    ["cluster_id", "company_id"]
)

output_path = OUTPUT_DIR / "cluster_labels.csv"

output.to_csv(
    output_path,
    index=False
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("CLUSTERING VALIDATION")
print("=" * 60)

print(f"Output rows       : {len(output)}")
print(f"Unique companies  : {output['company_id'].nunique()}")
print(
    f"Unique clusters   : "
    f"{output['cluster_id'].nunique()}"
)

print("\nCluster distribution:")
print(
    output["cluster_id"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nCluster names:")
print(
    output[
        ["cluster_id", "cluster_name"]
    ]
    .drop_duplicates()
    .sort_values("cluster_id")
    .to_string(index=False)
)

print("\nMissing cluster IDs:")
print(output["cluster_id"].isna().sum())

print("\nOutput saved:")
print(output_path)

if len(output) != 92:
    raise ValueError(
        f"Expected 92 output rows, found {len(output)}"
    )

if output["company_id"].nunique() != 92:
    raise ValueError(
        "Some companies are duplicated or missing."
    )

if output["cluster_id"].nunique() != 5:
    raise ValueError(
        "Expected exactly 5 clusters."
    )

if output["distance_from_centroid"].isna().any():
    raise ValueError(
        "Distance from centroid contains missing values."
    )

print("\nALL 92 COMPANIES SUCCESSFULLY CLUSTERED.")
print("Day 36 clustering complete.")
