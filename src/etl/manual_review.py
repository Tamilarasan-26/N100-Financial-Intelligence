import sqlite3
import pandas as pd
from pathlib import Path


DB_PATH = Path("db/nifty100.db")
OUTPUT_PATH = Path("output/manual_review.csv")


def main():
    connection = sqlite3.connect(DB_PATH)

    try:
        companies = pd.read_sql_query(
            """
            SELECT
                id,
                company_name,
                broad_sector,
                market_cap_category
            FROM companies
            ORDER BY RANDOM()
            LIMIT 5
            """,
            connection
        )

        review_records = []

        print("\nMANUAL DATA REVIEW")
        print("=" * 70)

        for _, company in companies.iterrows():
            company_id = company["id"]

            financial_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM financial_ratios
                WHERE company_id = ?
                """,
                (company_id,)
            ).fetchone()[0]

            price_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM stock_prices
                WHERE company_id = ?
                """,
                (company_id,)
            ).fetchone()[0]

            print(f"\nCompany: {company_id}")
            print(f"Name: {company['company_name']}")
            print(f"Sector: {company['broad_sector']}")
            print(f"Financial records: {financial_count}")
            print(f"Stock price records: {price_count}")

            status = (
                "PASS"
                if financial_count > 0 and price_count > 0
                else "REVIEW"
            )

            print(f"Review Status: {status}")

            review_records.append({
                "company_id": company_id,
                "company_name": company["company_name"],
                "financial_records": financial_count,
                "stock_price_records": price_count,
                "review_status": status
            })

        pd.DataFrame(review_records).to_csv(
            OUTPUT_PATH,
            index=False
        )

        print("\nManual review completed")
        print("Report:", OUTPUT_PATH)

    finally:
        connection.close()


if __name__ == "__main__":
    main()