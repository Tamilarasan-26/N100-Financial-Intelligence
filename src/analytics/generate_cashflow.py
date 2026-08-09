from pathlib import Path

import pandas as pd

from cashflow_kpis import (
    classify_capital_allocation,
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

cashflow = pd.read_excel(
    RAW_DIR / "cashflow.xlsx",
    header=1
)


ratios = pd.read_excel(
    RAW_DIR / "financial_ratios.xlsx"
)
sectors = pd.read_excel(
    RAW_DIR / "sectors.xlsx"
)
profit_loss = pd.read_excel(
    RAW_DIR / "profitandloss.xlsx",
    header=1
)
profit_loss["year"] = (
    profit_loss["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

profit_loss["year"] = pd.to_numeric(
    profit_loss["year"],
    errors="coerce"
)

profit_loss = profit_loss.dropna(
    subset=["year"]
)

profit_loss["year"] = profit_loss["year"].astype(int)
# -----------------------------
# Normalize Year Format
# -----------------------------

cashflow["year"] = (
    cashflow["year"]
    .astype(str)
    .str.extract(r"(\d+)$")[0]
    .astype(int)
)

cashflow["year"] = cashflow["year"].apply(
    lambda x: x if x >= 2000 else 2000 + x
)

ratios["year"] = (
    ratios["year"]
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

data = cashflow.merge(
    ratios,
    on=["company_id", "year"],
    how="left"
)

data = data.merge(
    profit_loss[["company_id", "year", "sales"]],
    on=["company_id", "year"],
    how="left"
)

data = data.merge(
    sectors[["company_id", "broad_sector"]],
    on="company_id",
    how="left"
)

results = []

for company, company_df in data.groupby("company_id"):

    company_df = company_df.sort_values("year")
    
    # -----------------------------
    # 5-Year FCF CAGR
    # -----------------------------

    fcf_history = (
        company_df[
            ["year", "free_cash_flow_cr"]
        ]
        .dropna()
        .sort_values("year")
    )

    fcf_cagr_5yr = None

    if len(fcf_history) >= 6:

        beginning_fcf = fcf_history.iloc[-6]["free_cash_flow_cr"]
        ending_fcf = fcf_history.iloc[-1]["free_cash_flow_cr"]

        if beginning_fcf > 0 and ending_fcf > 0:

            fcf_cagr_5yr = (
                (ending_fcf / beginning_fcf) ** (1 / 5) - 1
            ) * 100

    valid_rows = company_df[
        company_df["cash_from_operations_cr"].notna()
    ]

    if valid_rows.empty:
        continue

    latest = valid_rows.iloc[-1]

    classification = classify_capital_allocation(
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"]
    )
    fcf = free_cash_flow(
        latest["cash_from_operations_cr"],
        latest["capex_cr"]
    )

    cfo = cfo_quality_score(
        latest["cash_from_operations_cr"],
        latest["free_cash_flow_cr"]
    )

    capex = capex_intensity(
        latest["capex_cr"],
        latest["sales"]
    )
    
    # -----------------------------
    # CapEx Intensity Label
    # -----------------------------

    if capex is None:
        capex_label = "NOT_AVAILABLE"
    elif capex < 10:
        capex_label = "LOW"
    elif capex < 20:
        capex_label = "MODERATE"
    else:
        capex_label = "HIGH"

    fcf_conversion = fcf_conversion_rate(
        latest["free_cash_flow_cr"],
        latest["cash_from_operations_cr"]
    )
    distress_flag = (
        latest["operating_activity"] < 0
        and
        latest["financing_activity"] > 0
    )
    deleveraging_flag = (
        latest["financing_activity"] < 0
    )

    results.append({

        "company_id": company,

        "sector": latest["broad_sector"],

        "capital_allocation": classification,

        "capital_allocation_label": classification,

        "free_cash_flow": fcf,

        "cfo_quality_score": cfo.score,

        "cfo_quality_label": cfo.label,

        "capex_intensity_pct": capex,

        "capex_label": capex_label,

        "fcf_cagr_5yr": fcf_cagr_5yr,

        "fcf_conversion_pct": fcf_conversion,

        "distress_flag": distress_flag,

        "deleveraging_flag": deleveraging_flag
    })
    

output = pd.DataFrame(results)


output.to_excel(
    OUTPUT_DIR / "cashflow_intelligence.xlsx",
    index=False
)

distress = output[
    output["distress_flag"] == True
]

distress.to_csv(
    OUTPUT_DIR / "distress_alerts.csv",
    index=False
)

print(f"Distress Alerts: {len(distress)}")

print("Done!")
print(output.head())
