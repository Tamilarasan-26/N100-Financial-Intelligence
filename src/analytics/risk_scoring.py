from pathlib import Path

import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"

INPUT_FILE = OUTPUT_DIR / "cashflow_intelligence.xlsx"

df = pd.read_excel(INPUT_FILE)

print(df.head())
print(df.columns.tolist())

def calculate_risk_score(row):

    score = 0

    # -----------------------------
    # CFO Quality
    # -----------------------------
    if row["cfo_quality_label"] == "STRONG":
        score += 3
    elif row["cfo_quality_label"] == "ADEQUATE":
        score += 2
    else:
        score += 1

    # -----------------------------
    # Capital Allocation
    # -----------------------------
    if row["capital_allocation"] == "SELF_FUNDED_GROWTH":
        score += 3
    elif row["capital_allocation"] == "ASSET_SALE_AND_DELEVERAGING":
        score += 2
    else:
        score += 1

    # -----------------------------
    # Distress Flag
    # -----------------------------
    if row["distress_flag"]:
        score -= 3

    # -----------------------------
    # Deleveraging
    # -----------------------------
    if row["deleveraging_flag"]:
        score += 2

    return score

df["risk_score"] = df.apply(
    calculate_risk_score,
    axis=1
)

def risk_category(score):

    if score >= 7:
        return "LOW"

    elif score >= 4:
        return "MEDIUM"

    return "HIGH"
df["risk_category"] = df["risk_score"].apply(
    risk_category
)
risk_summary = (
    df["risk_category"]
    .value_counts()
    .reset_index()
)

risk_summary.columns = [
    "risk_category",
    "company_count"
]

print("\nRisk Summary")
print(risk_summary)

OUTPUT_FILE = OUTPUT_DIR / "risk_scores.xlsx"

df.to_excel(
    OUTPUT_FILE,
    index=False
)

print(df.head())

risk_summary.to_csv(
    OUTPUT_DIR / "risk_summary.csv",
    index=False
)

print("Risk scoring completed!")