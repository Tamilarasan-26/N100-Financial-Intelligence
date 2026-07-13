from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

failures = []


def add_failure(rule, table, severity, message):
    failures.append({
        "rule": rule,
        "table": table,
        "severity": severity,
        "message": message
    })


def load_data():
    data = {}

    for file in PROCESSED_DIR.glob("*.csv"):
        data[file.stem] = pd.read_csv(file)

    return data


def validate(data):
    companies = data["companies"]

    if companies["id"].duplicated().any():
        add_failure(
            "DQ-01",
            "companies",
            "CRITICAL",
            "Duplicate company IDs found"
        )

    for table_name, df in data.items():
        if "company_id" in df.columns:
            if df["company_id"].isna().any():
                add_failure(
                    "DQ-02",
                    table_name,
                    "CRITICAL",
                    "Null company_id found"
                )

    valid_companies = set(
        companies["id"].astype(str)
    )

    for table_name, df in data.items():
        if table_name != "companies" and "company_id" in df.columns:
            invalid = ~df["company_id"].astype(str).isin(
                valid_companies
            )

            if invalid.any():
                add_failure(
                    "DQ-03",
                    table_name,
                    "CRITICAL",
                    f"{invalid.sum()} invalid foreign keys"
                )

    balance = data["balancesheet"]

    if "total_assets" in balance.columns:
        if (balance["total_assets"] < 0).any():
            add_failure(
                "DQ-04",
                "balancesheet",
                "WARNING",
                "Negative total assets found"
            )

    pnl = data["profitandloss"]

    if "sales" in pnl.columns:
        if (pnl["sales"] <= 0).any():
            add_failure(
                "DQ-05",
                "profitandloss",
                "CRITICAL",
                "Non-positive sales found"
            )

    if "net_profit" in pnl.columns:
        if pnl["net_profit"].isna().any():
            add_failure(
                "DQ-06",
                "profitandloss",
                "WARNING",
                "Missing net profit values"
            )

    stock = data["stock_prices"]

    if stock["date"].isna().any():
        add_failure(
            "DQ-07",
            "stock_prices",
            "CRITICAL",
            "Missing stock price dates"
        )

    if (stock["close_price"] <= 0).any():
        add_failure(
            "DQ-08",
            "stock_prices",
            "CRITICAL",
            "Invalid closing prices"
        )

    if (stock["high_price"] < stock["low_price"]).any():
        add_failure(
            "DQ-09",
            "stock_prices",
            "CRITICAL",
            "High price lower than low price"
        )

    if (stock["volume"] < 0).any():
        add_failure(
            "DQ-10",
            "stock_prices",
            "WARNING",
            "Negative stock volume"
        )

    ratios = data["financial_ratios"]

    if ratios["debt_to_equity"].isna().any():
        add_failure(
            "DQ-11",
            "financial_ratios",
            "WARNING",
            "Missing debt-to-equity values"
        )

    if (ratios["interest_coverage"] < 0).any():
        add_failure(
            "DQ-12",
            "financial_ratios",
            "WARNING",
            "Negative interest coverage"
        )

    market = data["market_cap"]

    if (market["market_cap_crore"] <= 0).any():
        add_failure(
            "DQ-13",
            "market_cap",
            "CRITICAL",
            "Invalid market capitalization"
        )

    if (market["pe_ratio"] < 0).any():
        add_failure(
            "DQ-14",
            "market_cap",
            "WARNING",
            "Negative PE ratio"
        )

    sectors = data["sectors"]

    if sectors["broad_sector"].isna().any():
        add_failure(
            "DQ-15",
            "sectors",
            "WARNING",
            "Missing broad sector"
        )

    if sectors["company_id"].duplicated().any():
        add_failure(
            "DQ-16",
            "sectors",
            "WARNING",
            "Duplicate company sector records"
        )


def main():
    data = load_data()

    print("Tables loaded:", len(data))

    validate(data)

    output_file = OUTPUT_DIR / "validation_failures.csv"

    pd.DataFrame(
        failures,
        columns=[
            "rule",
            "table",
            "severity",
            "message"
        ]
    ).to_csv(output_file, index=False)

    critical_count = sum(
        failure["severity"] == "CRITICAL"
        for failure in failures
    )

    print("DQ rules executed: 16")
    print("Total failures:", len(failures))
    print("CRITICAL failures:", critical_count)
    print("Validation report:", output_file)


if __name__ == "__main__":
    main()