from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
VALIDATED_DIR = Path("data/validated")

VALIDATED_DIR.mkdir(parents=True, exist_ok=True)


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


def clean_foreign_keys(df, valid_companies):
    if "company_id" not in df.columns:
        return df

    company_ids = (
        df["company_id"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df[
        company_ids.isin(valid_companies)
    ].copy()


def clean_business_rules(df, table_name):
    if table_name == "profitandloss":
        df = df[
            df["sales"] > 0
        ].copy()

    return df


def main():
    valid_companies = load_valid_companies()

    files = sorted(
        PROCESSED_DIR.glob("*.csv")
    )

    print("Files found:", len(files))

    for file in files:
        table_name = file.stem

        df = pd.read_csv(file)

        original_rows = len(df)

        if table_name != "companies":
            df = clean_foreign_keys(
                df,
                valid_companies
            )

        df = clean_business_rules(
            df,
            table_name
        )

        validated_rows = len(df)
        rejected_rows = (
            original_rows - validated_rows
        )

        output_file = (
            VALIDATED_DIR
            / f"{table_name}.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print(
            f"{table_name}: "
            f"{original_rows} input | "
            f"{validated_rows} validated | "
            f"{rejected_rows} rejected"
        )

    print("\nValidated datasets created successfully")


if __name__ == "__main__":
    main()