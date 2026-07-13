from pathlib import Path
import pandas as pd

from normaliser import (
    normalize_year,
    normalize_ticker,
    normalize_columns,
)


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def detect_header(file_path):
    preview = pd.read_excel(
        file_path,
        header=None,
        nrows=2
    )

    first_value = str(preview.iloc[0, 0])

    if "Nifty 100" in first_value:
        return 1

    return 0


def load_excel(file_path):
    header_row = detect_header(file_path)

    df = pd.read_excel(
        file_path,
        header=header_row
    )

    df = normalize_columns(df)

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(
            normalize_ticker
        )

    if "year" in df.columns:
        df["year"] = df["year"].apply(
            normalize_year
        )

    return df


def save_processed(df, file_name):
    output_path = PROCESSED_DIR / f"{file_name}.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"{file_name}: {len(df)} rows processed"
    )


def main():
    excel_files = sorted(
        list(RAW_DIR.glob("*.xlsx"))
        + list(RAW_DIR.glob("*.xls"))
    )

    print("Excel files found:", len(excel_files))

    for file_path in excel_files:
        print("\nProcessing:", file_path.name)

        df = load_excel(file_path)

        save_processed(
            df,
            file_path.stem
        )

    print("\nETL processing completed")


if __name__ == "__main__":
    main()