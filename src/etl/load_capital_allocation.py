from pathlib import Path
import sqlite3

import pandas as pd


DB_PATH = Path("db/nifty100.db")
CSV_PATH = Path("output/capital_allocation.csv")


def main():

    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)

    try:

        df.to_sql(
            "capital_allocation",
            conn,
            if_exists="replace",
            index=False
        )

        count = conn.execute(
            "SELECT COUNT(*) FROM capital_allocation"
        ).fetchone()[0]

        print("Table created successfully.")
        print("Rows inserted:", count)

    finally:
        conn.close()


if __name__ == "__main__":
    main()