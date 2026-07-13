from pathlib import Path
import sqlite3
import pandas as pd


VALIDATED_DIR = Path("data/validated")
DB_PATH = Path("db/nifty100.db")
SCHEMA_PATH = Path("db/schema.sql")
AUDIT_PATH = Path("output/load_audit.csv")


def read_csv(name):
    return pd.read_csv(
        VALIDATED_DIR / f"{name}.csv"
    )


def create_database():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        connection.executescript(
            file.read()
        )

    return connection


def prepare_companies():
    companies = read_csv("companies")
    sectors = read_csv("sectors")

    sector_columns = [
        "company_id",
        "broad_sector",
        "sub_sector",
        "index_weight_pct",
        "market_cap_category"
    ]

    companies = companies.merge(
        sectors[sector_columns],
        left_on="id",
        right_on="company_id",
        how="left"
    )

    companies = companies.drop(
        columns=["company_id"]
    )

    return companies


def prepare_company_insights():
    analysis = read_csv("analysis")
    prosandcons = read_csv("prosandcons")

    analysis = analysis.drop(
        columns=["id"]
    )

    prosandcons = prosandcons.drop(
        columns=["id"]
    )

    insights = analysis.merge(
        prosandcons,
        on="company_id",
        how="outer"
    )

    return insights


def load_table(
    connection,
    table_name,
    dataframe
):
    input_rows = len(dataframe)

    dataframe.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )

    loaded_rows = connection.execute(
        f"SELECT COUNT(*) FROM {table_name}"
    ).fetchone()[0]

    print(
        f"{table_name}: "
        f"{input_rows} input | "
        f"{loaded_rows} loaded"
    )

    return {
        "table": table_name,
        "input_rows": input_rows,
        "loaded_rows": loaded_rows,
        "status": (
            "SUCCESS"
            if input_rows == loaded_rows
            else "MISMATCH"
        )
    }


def main():
    connection = create_database()

    audit_records = []

    try:
        companies = prepare_companies()

        company_insights = (
            prepare_company_insights()
        )

        tables = {
            "companies": companies,
            "company_insights": company_insights,
            "balancesheet": read_csv(
                "balancesheet"
            ),
            "cashflow": read_csv(
                "cashflow"
            ),
            "documents": read_csv(
                "documents"
            ),
            "financial_ratios": read_csv(
                "financial_ratios"
            ),
            "market_cap": read_csv(
                "market_cap"
            ),
            "peer_groups": read_csv(
                "peer_groups"
            ),
            "profitandloss": read_csv(
                "profitandloss"
            ),
            "stock_prices": read_csv(
                "stock_prices"
            )
        }

        for table_name, dataframe in tables.items():
            audit = load_table(
                connection,
                table_name,
                dataframe
            )

            audit_records.append(audit)

        connection.commit()

        foreign_key_errors = (
            connection.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()
        )

        print(
            "\nForeign key errors:",
            len(foreign_key_errors)
        )

        audit_df = pd.DataFrame(
            audit_records
        )

        AUDIT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        audit_df.to_csv(
            AUDIT_PATH,
            index=False
        )

        print(
            "Audit report:",
            AUDIT_PATH
        )

        print(
            "Database created:",
            DB_PATH
        )

        print(
            "\nDatabase load completed"
        )

    except Exception as error:
        connection.rollback()

        print(
            "\nDatabase load failed:"
        )

        print(error)

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()