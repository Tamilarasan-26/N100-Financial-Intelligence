from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"

cashflow = pd.read_excel(
    OUTPUT_DIR / "cashflow_intelligence.xlsx"
)

summary = (
    cashflow.groupby("capital_allocation")
    .size()
    .reset_index(name="company_count")
    .sort_values("company_count", ascending=False)
)

summary.to_csv(
    OUTPUT_DIR / "capital_allocation_summary.csv",
    index=False
)

print(summary)
print("Capital allocation summary generated!")