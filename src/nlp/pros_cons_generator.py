from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

ratios = pd.read_excel(
    RAW_DIR / "financial_ratios.xlsx"
)

print(ratios.head())

print(ratios.columns.tolist())

pros_cons = []

for company, company_df in ratios.groupby("company_id"):

    # Sort years
    company_df = company_df.sort_values("year")

    # Latest financial data
    latest = company_df.iloc[-1]
    if latest["return_on_equity_pct"] > 20:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P1",
            "text": "Return on Equity is above 20%, indicating strong profitability.",
            "confidence_pct": 95
        })
    if latest["debt_to_equity"] == 0:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P2",
            "text": "Debt-free balance sheet provides financial flexibility.",
            "confidence_pct": 90
        })
    if latest["free_cash_flow_cr"] > 0:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P3",
            "text": "Positive free cash flow indicates healthy cash generation.",
            "confidence_pct": 88
        })
    if latest["operating_profit_margin_pct"] > 20:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P4",
            "text": "Operating profit margin is above 20%, indicating strong operational efficiency.",
            "confidence_pct": 90
        })
    if latest["interest_coverage"] > 10:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P5",
            "text": "High interest coverage indicates comfortable debt servicing ability.",
            "confidence_pct": 89
        })
    if latest["asset_turnover"] > 1:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P6",
            "text": "Asset turnover above 1 reflects efficient utilization of assets.",
            "confidence_pct": 85
        })
    if latest["cash_from_operations_cr"] > 0:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P7",
            "text": "Positive cash from operations indicates strong operating cash generation.",
            "confidence_pct": 90
        })
    if latest["earnings_per_share"] > 0:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P8",
            "text": "Positive earnings per share reflects profitable business operations.",
            "confidence_pct": 88
        })  
    if latest["book_value_per_share"] > 0:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P9",
            "text": "Healthy book value per share indicates a strong asset base.",
            "confidence_pct": 85
        })
    if latest["dividend_payout_ratio_pct"] < 60:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P10",
            "text": "Moderate dividend payout leaves room for future growth.",
            "confidence_pct": 82
        })
    if latest["net_profit_margin_pct"] > 15:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P11",
            "text": "High net profit margin reflects strong profitability.",
            "confidence_pct": 91
        })
    if latest["total_debt_cr"] < 1000:

        pros_cons.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "P12",
            "text": "Low total debt reduces financial risk.",
            "confidence_pct": 84
        })
    if latest["debt_to_equity"] > 2:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C1",
            "text": "High debt-to-equity ratio indicates higher financial risk.",
            "confidence_pct": 90
        })
    if latest["free_cash_flow_cr"] < 0:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C2",
            "text": "Negative free cash flow raises concerns about cash generation.",
            "confidence_pct": 92
        })
    if latest["interest_coverage"] < 1.5:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C3",
            "text": "Interest coverage below 1.5 indicates debt servicing risk.",
            "confidence_pct": 94
        })
    if latest["operating_profit_margin_pct"] < 10:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C4",
            "text": "Low operating profit margin may affect long-term profitability.",
            "confidence_pct": 88
        })
    if latest["return_on_equity_pct"] < 10:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C5",
            "text": "Return on equity below 10% indicates weak shareholder returns.",
            "confidence_pct": 90
        })
    if latest["asset_turnover"] < 0.5:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C6",
            "text": "Low asset turnover suggests inefficient use of company assets.",
            "confidence_pct": 86
        })
    if latest["cash_from_operations_cr"] < 0:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C7",
            "text": "Negative cash from operations indicates weak operating cash generation.",
            "confidence_pct": 90
        })
    if latest["earnings_per_share"] < 0:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C8",
            "text": "Negative earnings per share indicates losses.",
            "confidence_pct": 95
        })
    if latest["book_value_per_share"] < 0:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C9",
            "text": "Negative book value indicates financial weakness.",
            "confidence_pct": 92
        })
    if latest["dividend_payout_ratio_pct"] > 80:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C10",
            "text": "Very high dividend payout may reduce future growth opportunities.",
            "confidence_pct": 85
        })
    if latest["net_profit_margin_pct"] < 5:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C11",
            "text": "Low net profit margin indicates weak profitability.",
            "confidence_pct": 88
        })
    if latest["total_debt_cr"] > 10000:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C12",
            "text": "High total debt increases financial risk.",
            "confidence_pct": 86
        })
    # ------------------------------------------------
    # Neutral fallback when no Con rule is triggered
    # ------------------------------------------------

    existing_cons = [
        item
        for item in pros_cons
        if item["company_id"] == company
        and item["type"] == "Con"
    ]

    if len(existing_cons) == 0:

        pros_cons.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "C13",
            "text": "No major financial risk flags were triggered under the current rule set.",
            "confidence_pct": 80
        })
pros_cons_df = pd.DataFrame(pros_cons)

pros_cons_df = pros_cons_df[
    pros_cons_df["confidence_pct"] > 60
]

company_summary = (
    pros_cons_df
    .groupby(["company_id", "type"])
    .size()
    .unstack(fill_value=0)
)

missing = company_summary[
    (company_summary.get("Pro", 0) == 0) |
    (company_summary.get("Con", 0) == 0)
]

print("\nCompanies missing Pro or Con:")
print(missing)

pros_cons_df.to_csv(
    OUTPUT_DIR / "pros_cons_generated.csv",
    index=False
)

print(pros_cons_df.head())
print(f"Generated {len(pros_cons_df)} Pros/Cons")

