from pathlib import Path
import pandas as pd

processed_dir = Path("data/processed")

companies = pd.read_csv(processed_dir / "companies.csv")

missing_ids = [
    "AGTL",
    "ULTRACEMCO",
    "UNIONBANK",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZOMATO",
    "ZYDUSLIFE"
]

print("COMPANIES COLUMNS:")
print(companies.columns.tolist())

print("\nMASTER COMPANY COUNT:")
print(len(companies))

print("\nPOSSIBLE MATCHES:")

keywords = [
    "ADANI",
    "ULTRA",
    "UNION",
    "UNITED",
    "VARUN",
    "VEDANTA",
    "WIPRO",
    "ZOMATO",
    "ZYDUS"
]

for keyword in keywords:
    print("\n", "=" * 50)
    print("KEYWORD:", keyword)

    mask = companies.astype(str).apply(
        lambda col: col.str.contains(
            keyword,
            case=False,
            na=False
        )
    ).any(axis=1)

    print(companies[mask].to_string(index=False))


referenced_ids = set()

for file in processed_dir.glob("*.csv"):

    if file.stem == "companies":
        continue

    df = pd.read_csv(file)

    if "company_id" in df.columns:
        referenced_ids.update(
            df["company_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.upper()
        )

master_ids = set(
    companies["id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print("\nMASTER IDs NOT REFERENCED BY OTHER TABLES:")
print(sorted(master_ids - referenced_ids))

print("\nMISSING IDs:")
print(missing_ids)