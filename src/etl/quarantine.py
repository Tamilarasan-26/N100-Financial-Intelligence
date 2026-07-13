from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
QUARANTINE_DIR = Path("output/quarantine")

QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


def load_valid_companies():
    companies = pd.read_csv(
        PROCESSED_DIR / "companies.csv"
    )

    return set(
        companies["id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )


def quarantine_foreign_keys(valid_companies):
    total_quarantined = 0

    for file in PROCESSED_DIR.glob("*.csv"):
        if file.stem == "companies":
            continue

        df = pd.read_csv(file)

        if "company_id" not in df.columns:
            continue

        company_ids = (
            df["company_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid_mask = ~company_ids.isin(valid_companies)

        invalid_rows = df[invalid_mask].copy()

        if not invalid_rows.empty:
            invalid_rows["dq_rule"] = "DQ-03"
            invalid_rows["failure_reason"] = (
                "company_id missing from companies master"
            )

            output_file = (
                QUARANTINE_DIR
                / f"{file.stem}_dq03.csv"
            )

            invalid_rows.to_csv(
                output_file,
                index=False
            )

            total_quarantined += len(invalid_rows)

            print(
                f"{file.stem}: "
                f"{len(invalid_rows)} FK rows quarantined"
            )

    return total_quarantined


def quarantine_invalid_sales():
    file = PROCESSED_DIR / "profitandloss.csv"

    df = pd.read_csv(file)

    invalid_mask = df["sales"] <= 0

    invalid_rows = df[invalid_mask].copy()

    if not invalid_rows.empty:
        invalid_rows["dq_rule"] = "DQ-05"
        invalid_rows["failure_reason"] = (
            "sales must be greater than zero"
        )

        output_file = (
            QUARANTINE_DIR
            / "profitandloss_dq05.csv"
        )

        invalid_rows.to_csv(
            output_file,
            index=False
        )

        print(
            f"profitandloss: "
            f"{len(invalid_rows)} sales rows quarantined"
        )

    return len(invalid_rows)


def main():
    valid_companies = load_valid_companies()

    fk_count = quarantine_foreign_keys(
        valid_companies
    )

    sales_count = quarantine_invalid_sales()

    print("\nQuarantine completed")
    print("FK rows quarantined:", fk_count)
    print("Sales rows quarantined:", sales_count)
    print(
        "Total quarantined rows:",
        fk_count + sales_count
    )


if __name__ == "__main__":
    main()