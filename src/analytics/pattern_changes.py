from pathlib import Path

import pandas as pd

from cashflow_kpis import classify_capital_allocation


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD FINAL 92-COMPANY UNIVERSE
# ============================================================

risk_scores = pd.read_excel(
    OUTPUT_DIR / "risk_scores.xlsx"
)

company_universe = set(
    risk_scores["company_id"]
    .dropna()
    .astype(str)
    .str.strip()
)


# ============================================================
# LOAD RAW CASH-FLOW DATA
# ============================================================

cashflow = pd.read_excel(
    RAW_DIR / "cashflow.xlsx",
    header=1
)

cashflow["company_id"] = (
    cashflow["company_id"]
    .astype(str)
    .str.strip()
)


# ============================================================
# FILTER TO FINAL 92-COMPANY UNIVERSE
# ============================================================

cashflow = cashflow[
    cashflow["company_id"].isin(company_universe)
].copy()


# ============================================================
# NORMALIZE YEAR
# ============================================================

cashflow["year"] = (
    cashflow["year"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
)

cashflow["year"] = pd.to_numeric(
    cashflow["year"],
    errors="coerce"
)

cashflow = cashflow.dropna(
    subset=["year"]
).copy()

cashflow["year"] = cashflow["year"].astype(int)

cashflow["year"] = cashflow["year"].apply(
    lambda x: x if x >= 2000 else 2000 + x
)


# ============================================================
# GENERATE PATTERN CHANGES
# ============================================================

results = []

for company, df in cashflow.groupby("company_id"):

    df = df.sort_values("year").copy()

    df["capital_allocation"] = df.apply(
        lambda row: classify_capital_allocation(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        ),
        axis=1
    )

    if df.empty:
        continue

    previous_pattern = df.iloc[0]["capital_allocation"]
    latest_pattern = df.iloc[-1]["capital_allocation"]

    results.append(
        {
            "company_id": company,
            "previous_pattern": previous_pattern,
            "latest_pattern": latest_pattern,
            "changed": previous_pattern != latest_pattern,
        }
    )


# ============================================================
# CREATE OUTPUT
# ============================================================

output = pd.DataFrame(results)

output = output.sort_values(
    "company_id"
).reset_index(drop=True)

output.to_csv(
    OUTPUT_DIR / "pattern_changes.csv",
    index=False
)


# ============================================================
# VALIDATION
# ============================================================

print(output.head(10).to_string(index=False))

print(f"\nFinal Company Universe : {len(company_universe)}")
print(f"Pattern Change Rows    : {len(output)}")
print(f"Unique Companies       : {output['company_id'].nunique()}")
print(f"Pattern Changed        : {output['changed'].sum()}")
print(f"Pattern Unchanged      : {(~output['changed']).sum()}")

missing = sorted(
    company_universe - set(output["company_id"])
)

if missing:
    print("\nWARNING - Companies Missing:")
    print(missing)
else:
    print("\nAll 92 companies successfully processed.")

print("\nPattern changes report generated!")