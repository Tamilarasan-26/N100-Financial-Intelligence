from fastapi import APIRouter, HTTPException
import sqlite3

from src.api.main import DB_PATH


router = APIRouter()


# ============================================================
# GET COMPANIES IN A PEER GROUP
# ============================================================

@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):
    """
    Return all companies in a peer group with percentile
    ranks for the 10 peer metrics.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. CHECK WHETHER PEER GROUP EXISTS
        # ----------------------------------------------------

        group_row = connection.execute(
            """
            SELECT 1
            FROM peer_groups
            WHERE peer_group_name = ?
            LIMIT 1
            """,
            (group_name,),
        ).fetchone()

        if group_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Peer group '{group_name}' not found.",
            )

        # ----------------------------------------------------
        # 2. GET COMPANIES IN PEER GROUP
        # ----------------------------------------------------

        company_rows = connection.execute(
            """
            SELECT
                pg.company_id,
                pg.is_benchmark,
                c.company_name,
                c.broad_sector,
                c.sub_sector,
                c.market_cap_category

            FROM peer_groups pg

            LEFT JOIN companies c
                ON pg.company_id = c.id

            WHERE pg.peer_group_name = ?

            ORDER BY
                pg.is_benchmark DESC,
                c.company_name
            """,
            (group_name,),
        ).fetchall()

        # ----------------------------------------------------
        # 3. GET LATEST YEAR
        # ----------------------------------------------------

        latest_year_row = connection.execute(
            """
            SELECT MAX(year) AS latest_year
            FROM peer_percentiles
            WHERE peer_group_name = ?
            """,
            (group_name,),
        ).fetchone()

        latest_year = (
            latest_year_row["latest_year"]
            if latest_year_row
            else None
        )

        # ----------------------------------------------------
        # 4. GET PEER PERCENTILE DATA
        # ----------------------------------------------------

        percentile_rows = connection.execute(
            """
            SELECT
                company_id,
                metric,
                value,
                percentile_rank

            FROM peer_percentiles

            WHERE peer_group_name = ?
              AND year = ?

            ORDER BY company_id, metric
            """,
            (
                group_name,
                latest_year,
            ),
        ).fetchall()

        # ----------------------------------------------------
        # 5. ORGANIZE METRICS BY COMPANY
        # ----------------------------------------------------

        company_metrics = {}

        for row in percentile_rows:

            company_id = row["company_id"]

            if company_id not in company_metrics:
                company_metrics[company_id] = {}

            company_metrics[company_id][row["metric"]] = {
                "value": row["value"],
                "percentile_rank": row["percentile_rank"],
            }

        # ----------------------------------------------------
        # 6. BUILD COMPANY RESPONSE
        # ----------------------------------------------------

        companies = []

        for row in company_rows:

            company_id = row["company_id"]

            companies.append({
                "company_id": company_id,
                "company_name": row["company_name"],
                "broad_sector": row["broad_sector"],
                "sub_sector": row["sub_sector"],
                "market_cap_category":
                    row["market_cap_category"],
                "is_benchmark":
                    bool(row["is_benchmark"]),
                "metrics":
                    company_metrics.get(
                        company_id,
                        {}
                    ),
            })

        # ----------------------------------------------------
        # 7. RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "peer_group": group_name,
            "year": latest_year,
            "count": len(companies),
            "companies": companies,
        }

    finally:
        connection.close()


# ============================================================
# PEER COMPARISON
# ============================================================

@router.get("/companies/{ticker}/peers/compare")
def compare_company_with_peers(ticker: str):
    """
    Return radar comparison data for a company,
    peer-group average, and benchmark company.
    """

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        # ----------------------------------------------------
        # 1. CHECK WHETHER COMPANY EXISTS
        # ----------------------------------------------------

        company_row = connection.execute(
            """
            SELECT
                id,
                company_name,
                broad_sector,
                sub_sector,
                market_cap_category
            FROM companies
            WHERE id = ?
            LIMIT 1
            """,
            (ticker.upper(),),
        ).fetchone()

        if company_row is None:

            raise HTTPException(
                status_code=404,
                detail=f"Company '{ticker}' not found.",
            )

        company_id = company_row["id"]

        # ----------------------------------------------------
        # 2. FIND COMPANY PEER GROUP
        # ----------------------------------------------------

        peer_group_row = connection.execute(
            """
            SELECT
                peer_group_name,
                is_benchmark
            FROM peer_groups
            WHERE company_id = ?
            ORDER BY is_benchmark DESC
            LIMIT 1
            """,
            (company_id,),
        ).fetchone()

        if peer_group_row is None:

            raise HTTPException(
                status_code=404,
                detail=f"No peer group found for '{ticker}'.",
            )

        peer_group = peer_group_row["peer_group_name"]

        # ----------------------------------------------------
        # 3. GET LATEST PEER YEAR
        # ----------------------------------------------------

        year_row = connection.execute(
            """
            SELECT MAX(year) AS latest_year
            FROM peer_percentiles
            WHERE peer_group_name = ?
            """,
            (peer_group,),
        ).fetchone()

        latest_year = year_row["latest_year"]

        if latest_year is None:

            raise HTTPException(
                status_code=404,
                detail=f"No peer data found for '{peer_group}'.",
            )

        # ----------------------------------------------------
        # 4. EIGHT RADAR METRICS
        # ----------------------------------------------------

        radar_metrics = [
            "ROE",
            "ROCE",
            "Net Profit Margin",
            "Revenue CAGR 5Y",
            "PAT CAGR 5Y",
            "EPS CAGR 5Y",
            "Debt To Equity",
            "Interest Coverage",
        ]

        # ----------------------------------------------------
        # 5. GET COMPANY PEER-GROUP MEMBERS
        # ----------------------------------------------------

        peer_company_rows = connection.execute(
            """
            SELECT
                company_id,
                is_benchmark
            FROM peer_groups
            WHERE peer_group_name = ?
            """,
            (peer_group,),
        ).fetchall()

        peer_company_ids = [
            row["company_id"]
            for row in peer_company_rows
        ]

        # ----------------------------------------------------
        # 6. FIND BENCHMARK COMPANY
        # ----------------------------------------------------

        benchmark_id = None

        for row in peer_company_rows:

            if row["is_benchmark"] == 1:
                benchmark_id = row["company_id"]
                break

        # ----------------------------------------------------
        # 7. GET ALL METRIC VALUES
        # ----------------------------------------------------

        placeholders = ",".join(
            ["?"] * len(peer_company_ids)
        )

        query = f"""
        SELECT
            company_id,
            metric,
            value
        FROM peer_percentiles
        WHERE peer_group_name = ?
          AND year = ?
          AND company_id IN ({placeholders})
        """

        params = [
            peer_group,
            latest_year,
            *peer_company_ids,
        ]

        metric_rows = connection.execute(
            query,
            params,
        ).fetchall()

        # ----------------------------------------------------
        # 8. ORGANIZE VALUES
        # ----------------------------------------------------

        metric_values = {}

        for row in metric_rows:

            company_id_key = row["company_id"]
            metric = row["metric"]

            if company_id_key not in metric_values:
                metric_values[company_id_key] = {}

            metric_values[company_id_key][metric] = row["value"]

        # ----------------------------------------------------
        # 9. CALCULATE COMPARISON
        # ----------------------------------------------------

        comparison = []

        for metric in radar_metrics:

            company_value = metric_values.get(
                company_id,
                {}
            ).get(metric)

            benchmark_value = None

            if benchmark_id is not None:

                benchmark_value = metric_values.get(
                    benchmark_id,
                    {}
                ).get(metric)

            # ----------------------------------------------
            # Peer average
            # ----------------------------------------------

            peer_values = []

            for peer_id in peer_company_ids:

                value = metric_values.get(
                    peer_id,
                    {}
                ).get(metric)

                if value is not None:
                    peer_values.append(value)

            peer_average = None

            if peer_values:

                peer_average = round(
                    sum(peer_values) / len(peer_values),
                    2,
                )

            # ----------------------------------------------
            # Add comparison
            # ----------------------------------------------

            comparison.append({
                "metric": metric,
                "company": company_value,
                "peer_average": peer_average,
                "benchmark": benchmark_value,
            })

        # ----------------------------------------------------
        # 10. GET BENCHMARK COMPANY NAME
        # ----------------------------------------------------

        benchmark_name = None

        if benchmark_id is not None:

            benchmark_row = connection.execute(
                """
                SELECT company_name
                FROM companies
                WHERE id = ?
                LIMIT 1
                """,
                (benchmark_id,),
            ).fetchone()

            if benchmark_row:

                benchmark_name = benchmark_row[
                    "company_name"
                ]

        # ----------------------------------------------------
        # 11. RETURN RESPONSE
        # ----------------------------------------------------

        return {
            "company_id": company_id,
            "company_name": company_row["company_name"],
            "peer_group": peer_group,
            "year": latest_year,

            "benchmark": {
                "company_id": benchmark_id,
                "company_name": benchmark_name,
            },

            "metrics": comparison,
        }

    finally:
        connection.close()