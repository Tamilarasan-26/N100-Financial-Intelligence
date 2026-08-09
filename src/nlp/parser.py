import re
from pathlib import Path
import sqlite3
import pandas as pd

# -----------------------------
# Paths
# -----------------------------
RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

INPUT_FILE = RAW_DIR / "analysis.xlsx"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"

def load_financial_ratios():

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        """
        SELECT
            company_id,
            revenue_cagr_5y_pct,
            pat_cagr_5y_pct
        FROM financial_ratios
        WHERE period_type='ANNUAL'
        """,
        con
    )

    con.close()

    return df

# -----------------------------
# Read Excel
# -----------------------------
df = pd.read_excel(INPUT_FILE, header=1)

# -----------------------------
# Regex Patterns
# -----------------------------
patterns = [
    r"(\d+)\s*Years?:?\s*(-?[\d.]+)%",
    r"(\d+)\s*Year:?\s*(-?[\d.]+)%",
    r"Last\s*Year:?\s*(-?[\d.]+)%",
    r"TTM:?\s*(-?[\d.]+)%"
]

# -----------------------------
# Columns to Parse
# -----------------------------
target_columns = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]

parsed_rows = []
failed_rows = []

# -----------------------------
# Parse Loop
# -----------------------------
for _, row in df.iterrows():

    company = row["company_id"]

    for metric in target_columns:

        value = str(row[metric]).strip()

        matched = False

        # -------------------------
        # 10 Years / 5 Years etc.
        # -------------------------
        m = re.search(patterns[0], value)

        if m:
            parsed_rows.append({
                "company_id": company,
                "metric_type": metric,
                "period_years": int(m.group(1)),
                "value_pct": float(m.group(2))
            })
            matched = True

        # -------------------------
        # Last Year
        # -------------------------
        if not matched:
            m = re.search(patterns[2], value)

            if m:
                parsed_rows.append({
                    "company_id": company,
                    "metric_type": metric,
                    "period_years": 1,
                    "value_pct": float(m.group(1))
                })
                matched = True

        # -------------------------
        # TTM
        # -------------------------
        if not matched:
            m = re.search(patterns[3], value)

            if m:
                parsed_rows.append({
                    "company_id": company,
                    "metric_type": metric,
                    "period_years": "TTM",
                    "value_pct": float(m.group(1))
                })
                matched = True

        # -------------------------
        # Failed Parsing
        # -------------------------
        if not matched:

            failed_rows.append({
                "company_id": company,
                "metric": metric,
                "original_text": value
            })

# -----------------------------
# Save Outputs
# -----------------------------
parsed_df = pd.DataFrame(parsed_rows)

failed_df = pd.DataFrame(failed_rows)

parsed_df.to_csv(
    OUTPUT_DIR / "analysis_parsed.csv",
    index=False
)

failed_df.to_csv(
    OUTPUT_DIR / "parse_failures.csv",
    index=False
)

print("Done!")
print(f"Parsed Rows : {len(parsed_df)}")
print(f"Failed Rows : {len(failed_df)}")

# -----------------------------
# Cross Validation
# -----------------------------

ratio_df = load_financial_ratios()

comparison = parsed_df[
    parsed_df["period_years"] == 5
].copy()

metric_map = {
    "compounded_sales_growth": "revenue_cagr_5y_pct",
    "compounded_profit_growth": "pat_cagr_5y_pct"
}

manual_review = []

for _, row in comparison.iterrows():

    metric = row["metric_type"]

    if metric not in metric_map:
        continue

    ratio_column = metric_map[metric]

    match = ratio_df[
        ratio_df["company_id"] == row["company_id"]
    ]

    if match.empty:
        continue

    ratio_value = match.iloc[0][ratio_column]

    if pd.isna(ratio_value):
        continue

    difference = abs(
        row["value_pct"] - ratio_value
    )

    if difference > 5:

        manual_review.append({
            "company_id": row["company_id"],
            "metric": metric,
            "parsed_value": row["value_pct"],
            "ratio_engine_value": ratio_value,
            "difference": difference
        })

manual_review_df = pd.DataFrame(manual_review)

manual_review_df.to_csv(
    OUTPUT_DIR / "manual_review.csv",
    index=False
)

print(
    f"Manual Review Rows : {len(manual_review_df)}"
)