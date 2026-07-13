import sqlite3
from pathlib import Path


DB_PATH = Path("db/nifty100.db")


def main():
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        print("Total tables:", len(tables))

        print("\nTABLE ROW COUNTS")

        for table in tables:
            table_name = table[0]

            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            print(f"{table_name}: {count}")

        fk_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print("\nForeign key errors:", len(fk_errors))

        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        print("Database integrity:", integrity)

        print("\nDatabase verification completed")

    finally:
        connection.close()


if __name__ == "__main__":
    main()