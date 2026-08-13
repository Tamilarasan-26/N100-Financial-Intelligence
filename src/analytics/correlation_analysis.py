from pathlib import Path
import sqlite3

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REPORT_DIR / "correlation_heatmap.png"


# ============================================================
# CORE FINANCIAL KPIs
# ============================================================

KPIS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "pat_cagr_5y_pct",
    "operating_profit_margin_pct",
    "interest_coverage",
    "free_cash_flow_cr",
    "asset_turnover",
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
}


# ============================================================
# START
# ============================================================

print("=" * 60)
print("CORRELATION ANALYSIS")
print("=" * 60)


# ============================================================
# DATABASE CHECK
# ============================================================

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Database not found: {DB_PATH}"
    )


# ============================================================
# LOAD DATA
# ============================================================

con = sqlite3.connect(DB_PATH)

query = """
SELECT
    company_id,
    year,
    period_type,
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
"""

financials = pd.read_sql(query, con)

con.close()


# ============================================================
# NORMALIZE TYPES
# ============================================================

financials["company_id"] = (
    financials["company_id"]
    .astype(str)
    .str.strip()
)

financials["year"] = pd.to_numeric(
    financials["year"],
    errors="coerce"
)

financials = financials.dropna(
    subset=["year"]
)

financials["year"] = (
    financials["year"]
    .astype(int)
)


# ============================================================
# SELECT LATEST YEAR PER COMPANY
# ============================================================

latest = (
    financials
    .sort_values(
        ["company_id", "year"]
    )
    .groupby(
        "company_id",
        as_index=False
    )
    .tail(1)
    .copy()
)


# ============================================================
# VALIDATE COMPANY UNIVERSE
# ============================================================

company_count = latest["company_id"].nunique()

print(
    f"Companies loaded : {company_count}"
)

print(
    f"Latest rows      : {len(latest)}"
)


# ============================================================
# CHECK KPI COLUMNS
# ============================================================

missing_kpis = [
    column
    for column in KPIS
    if column not in latest.columns
]

if missing_kpis:
    raise ValueError(
        f"Missing KPI columns: {missing_kpis}"
    )


# ============================================================
# MISSING VALUE CHECK
# ============================================================

print("\nMissing values before correlation:")

missing_values = (
    latest[KPIS]
    .isna()
    .sum()
)

print(
    missing_values.to_string()
)


# ============================================================
# CORRELATION DATA
# ============================================================

corr_data = latest[
    ["company_id"] + KPIS
].copy()


corr_data = corr_data.dropna(
    subset=KPIS
).copy()


print(
    f"\nComplete KPI rows : {len(corr_data)}"
)


# ============================================================
# PEARSON CORRELATION
# ============================================================

correlation = (
    corr_data[KPIS]
    .corr(method="pearson")
)


# ============================================================
# RENAME FOR DISPLAY
# ============================================================

correlation_display = correlation.rename(
    index=KPI_LABELS,
    columns=KPI_LABELS
)


# ============================================================
# PRINT MATRIX
# ============================================================

print("\nPearson Correlation Matrix:")

print(
    correlation_display
    .round(2)
    .to_string()
)


# ============================================================
# HEATMAP
# ============================================================

plt.figure(
    figsize=(11, 9)
)

sns.heatmap(
    correlation_display,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={
        "label": "Pearson Correlation"
    },
)


plt.title(
    "Pearson Correlation of Financial KPIs",
    fontsize=14,
    pad=15,
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.yticks(
    rotation=0
)

plt.tight_layout()


# ============================================================
# SAVE
# ============================================================

plt.savefig(
    OUTPUT_FILE,
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL VALIDATION
# ============================================================

if not OUTPUT_FILE.exists():
    raise FileNotFoundError(
        f"Heatmap was not created: {OUTPUT_FILE}"
    )


print(
    "\nCorrelation heatmap saved:"
)

print(OUTPUT_FILE)

print(
    "\nFinal validation:"
)

print(
    f"Companies analyzed : {len(latest)}"
)

print(
    f"Complete KPI rows  : {len(corr_data)}"
)

print(
    f"KPIs analyzed      : {len(KPIS)}"
)

print(
    f"Matrix shape       : {correlation.shape}"
)

print(
    "\nDay 37 — Correlation analysis complete."
)