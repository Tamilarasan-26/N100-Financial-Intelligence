from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

risk_df = pd.read_excel(
    PROJECT_ROOT / "output" / "risk_scores.xlsx"
)

sector_df = pd.read_excel(
    PROJECT_ROOT / "data" / "raw" / "sectors.xlsx"
)

df = risk_df.merge(
    sector_df,
    on="company_id",
    how="left"
)

# -----------------------------
# Portfolio Statistics
# -----------------------------

total_companies = len(df)

avg_risk_score = df["risk_score"].mean()

avg_cfo_score = df["cfo_quality_score"].mean()

avg_fcf_conversion = df["fcf_conversion_pct"].mean()

low_risk = len(df[df["risk_category"] == "LOW"])
medium_risk = len(df[df["risk_category"] == "MEDIUM"])
high_risk = len(df[df["risk_category"] == "HIGH"])

highest_risk = df.loc[df["risk_score"].idxmax()]

lowest_risk = df.loc[df["risk_score"].idxmin()]

print("\n========== Portfolio Summary ==========")
print(f"Total Companies        : {total_companies}")
print(f"Average Risk Score     : {avg_risk_score:.2f}")
print(f"Average CFO Score      : {avg_cfo_score:.2f}")
print(f"Average FCF Conversion : {avg_fcf_conversion:.2f}%")

print("\nRisk Distribution")
print(f"LOW    : {low_risk}")
print(f"MEDIUM : {medium_risk}")
print(f"HIGH   : {high_risk}")

print("\nHighest Risk Company")
print(
    f"{highest_risk['company_id']} "
    f"(Risk Score: {highest_risk['risk_score']})"
)

print("\nLowest Risk Company")
print(
    f"{lowest_risk['company_id']} "
    f"(Risk Score: {lowest_risk['risk_score']})"
)

print("=======================================")