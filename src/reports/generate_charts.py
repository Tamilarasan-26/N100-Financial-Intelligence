from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHART_DIR = PROJECT_ROOT / "reports" / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(
    RAW_DIR / "financial_ratios.xlsx"
)

for company_id in df["company_id"].unique():

    company = df[
        df["company_id"] == company_id
    ].sort_values("year")

    print(f"Generating charts for {company_id}")

    plt.figure(figsize=(6, 3))

    plt.plot(
        company["year"],
        company["return_on_equity_pct"],
        marker="o"
    )

    plt.title(f"{company_id} ROE Trend")
    plt.xlabel("Year")
    plt.ylabel("ROE (%)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_roe.png"
    )

    plt.close()

    plt.figure(figsize=(6, 3))

    plt.plot(
        company["year"],
        company["free_cash_flow_cr"],
        marker="o"
    )

    plt.title("TCS Free Cash Flow Trend")
    plt.xlabel("Year")
    plt.ylabel("Free Cash Flow (Cr)")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_fcf.png"
    )

    plt.close()

    # -----------------------------
    # Debt to Equity Trend
    # -----------------------------

    plt.figure(figsize=(6, 3))

    plt.plot(
        company["year"],
        company["debt_to_equity"],
        marker="o"
    )

    plt.title("TCS Debt-to-Equity Trend")
    plt.xlabel("Year")
    plt.ylabel("Debt-to-Equity")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_debt_equity.png"
    )

    plt.close()

    # -----------------------------
    # Interest Coverage Trend
    # -----------------------------

    plt.figure(figsize=(6, 3))

    plt.plot(
        company["year"],
        company["interest_coverage"],
        marker="o"
    )

    plt.title("TCS Interest Coverage Trend")
    plt.xlabel("Year")
    plt.ylabel("Interest Coverage")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_interest_coverage.png"
    )

    plt.close()

    # -----------------------------
    # Earnings Per Share Trend
    # -----------------------------

    plt.figure(figsize=(6, 3))

    plt.plot(
        company["year"],
        company["earnings_per_share"],
        marker="o"
    )

    plt.title("TCS Earnings Per Share Trend")
    plt.xlabel("Year")
    plt.ylabel("EPS")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_eps.png"
    )

    plt.close()

    print("Chart Generated Successfully!")

    # -----------------------------
    # Load Balance Sheet Data
    # -----------------------------

    # -----------------------------
    # Balance Sheet Trend
    # -----------------------------

    balance_df = pd.read_excel(
        RAW_DIR / "balancesheet.xlsx",
        header=1
    )

    balance_company = balance_df[
        balance_df["company_id"] == company_id
    ].sort_values("year")

    plt.figure(figsize=(6, 3))

    plt.plot(
        balance_company["year"],
        balance_company["total_assets"],
        marker="o",
        label="Total Assets"
    )

    plt.plot(
        balance_company["year"],
        balance_company["total_liabilities"],
        marker="o",
        label="Total Liabilities"
    )

    plt.plot(
        balance_company["year"],
        balance_company["equity_capital"],
        marker="o",
        label="Equity Capital"
    )

    plt.title("TCS Balance Sheet Trend")
    plt.xlabel("Year")
    plt.ylabel("Amount (Cr)")

    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_balance_sheet.png"
    )

    plt.close()

    # -----------------------------
    # Cash Flow Components Chart
    # -----------------------------

    cashflow_df = pd.read_excel(
        RAW_DIR / "cashflow.xlsx",
        header=1
    )

    cashflow_company = cashflow_df[
        cashflow_df["company_id"] == company_id
    ].sort_values("year")

    latest = cashflow_company.iloc[-1]

    labels = [
        "Operating",
        "Investing",
        "Financing",
        "Net Cash"
    ]

    values = [
        latest["operating_activity"],
        latest["investing_activity"],
        latest["financing_activity"],
        latest["net_cash_flow"]
    ]

    plt.figure(figsize=(7, 4))

    plt.bar(
        labels,
        values
    )

    plt.title("TCS Cash Flow Components")
    plt.ylabel("Amount (Cr)")

    plt.tight_layout()

    plt.savefig(
        CHART_DIR / f"{company_id}_cashflow.png"
    )

    plt.close()

    print("Chart Generated Successfully!")