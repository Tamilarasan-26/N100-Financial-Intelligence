from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHART_DIR = PROJECT_ROOT / "reports" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(
    PROJECT_ROOT / "output" / "risk_scores.xlsx"
)

# -----------------------------
# Risk Category Distribution
# -----------------------------

risk_counts = df["risk_category"].value_counts()

plt.figure(figsize=(6,4))

plt.bar(
    risk_counts.index,
    risk_counts.values
)

plt.title("Risk Category Distribution")
plt.xlabel("Risk Category")
plt.ylabel("Number of Companies")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "portfolio_risk_distribution.png"
)

plt.close()

print("Portfolio Risk Distribution Chart Generated!")

# -----------------------------
# Capital Allocation Distribution
# -----------------------------

allocation_counts = df["capital_allocation"].value_counts()

plt.figure(figsize=(7, 4))

plt.bar(
    allocation_counts.index,
    allocation_counts.values
)

plt.title("Capital Allocation Distribution")
plt.xlabel("Capital Allocation")
plt.ylabel("Number of Companies")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    CHART_DIR / "portfolio_capital_allocation.png"
)

plt.close()

print("Portfolio Capital Allocation Chart Generated!")

# -----------------------------
# Sector Distribution Chart
# -----------------------------

sector_df = pd.read_excel(
    PROJECT_ROOT / "data" / "raw" / "sectors.xlsx"
)

sector_counts = sector_df["broad_sector"].value_counts()

plt.figure(figsize=(8, 5))

plt.bar(
    sector_counts.index,
    sector_counts.values
)

plt.title("Sector Distribution")
plt.xlabel("Sector")
plt.ylabel("Number of Companies")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "portfolio_sector_distribution.png"
)

plt.close()

print("Portfolio Sector Distribution Chart Generated!")

# -----------------------------
# Top 10 Highest Risk Companies
# -----------------------------

top_risk = df.sort_values(
    "risk_score",
    ascending=False
).head(10)

plt.figure(figsize=(8, 5))

plt.bar(
    top_risk["company_id"],
    top_risk["risk_score"]
)

plt.title("Top 10 Highest Risk Companies")
plt.xlabel("Company")
plt.ylabel("Risk Score")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "portfolio_top10_risk.png"
)

plt.close()

print("Top 10 Risk Chart Generated!")

# -----------------------------
# Top 10 Lowest Risk Companies
# -----------------------------

lowest_risk = df.sort_values(
    "risk_score",
    ascending=True
).head(10)

plt.figure(figsize=(8, 5))

plt.bar(
    lowest_risk["company_id"],
    lowest_risk["risk_score"]
)

plt.title("Top 10 Lowest Risk Companies")
plt.xlabel("Company")
plt.ylabel("Risk Score")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "portfolio_top10_low_risk.png"
)

plt.close()

print("Top 10 Lowest Risk Chart Generated!")