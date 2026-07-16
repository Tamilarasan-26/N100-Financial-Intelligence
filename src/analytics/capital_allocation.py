from pathlib import Path
import sqlite3

import pandas as pd

from cashflow_kpis import classify_capital_allocation


DB_PATH = Path("db/nifty100.db")

OUTPUT_PATH = Path(
    "output/capital_allocation.csv"
)


# ---------------------------------------------------
# Load Cash Flow Data
# ---------------------------------------------------
def load_cashflow_data(connection):

    query = """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        ORDER BY company_id, year
    """

    return pd.read_sql_query(
        query,
        connection
    )


# ---------------------------------------------------
# Create Capital Allocation Report
# ---------------------------------------------------
def create_capital_allocation_report(dataframe):

    report = dataframe.copy()

    report[
        "capital_allocation_pattern"
    ] = report.apply(
        lambda row: classify_capital_allocation(
            operating_cash_flow=row[
                "operating_activity"
            ],
            investing_cash_flow=row[
                "investing_activity"
            ],
            financing_cash_flow=row[
                "financing_activity"
            ]
        ),
        axis=1
    )

    return report


# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():

    if not DB_PATH.exists():

        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(
        DB_PATH
    )

    try:

        cashflow = load_cashflow_data(
            connection
        )

        report = create_capital_allocation_report(
            cashflow
        )

        OUTPUT_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        report.to_csv(
            OUTPUT_PATH,
            index=False
        )

        print(
            "\nCapital Allocation Report Created Successfully"
        )

        print(
            "\nRows:",
            len(report)
        )

        print(
            "\nColumns:"
        )

        print(
            report.columns.tolist()
        )

        print(
            "\nPattern Counts"
        )

        print(
            report[
                "capital_allocation_pattern"
            ].value_counts(
                dropna=False
            )
        )

        print(
            "\nSaved to:"
        )

        print(
            OUTPUT_PATH
        )

    finally:

        connection.close()


if __name__ == "__main__":

    main()
    
