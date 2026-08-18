from pathlib import Path
import sqlite3
import sys
import logging
from dataclasses import dataclass

import pandas as pd


# ==========================================================
# Edge Case Logger
# ==========================================================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=OUTPUT_DIR / "ratio_edge_cases.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w"
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    low_interest_coverage_flag,
    asset_turnover,
)


from src.analytics.cagr import (
    calculate_growth_cagrs,
)


from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
)


DB_PATH = (
    PROJECT_ROOT
    / "db"
    / "nifty100.db"
)


RATIO_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "financial_ratios.csv"
)


def load_table(
    connection,
    table_name
):
    return pd.read_sql_query(
        f"SELECT * FROM {table_name}",
        connection
    )


def clean_year(
    dataframe
):
    dataframe = dataframe.copy()

    dataframe = dataframe[
        dataframe["year"].notna()
    ].copy()

    dataframe["year"] = (
        dataframe["year"]
        .astype(int)
    )

    return dataframe


def select_annual_record(
    dataframe
):
    """
    Create one deterministic annual record for each
    company_id + year.

    Rules:
    1. Remove missing years.
    2. Remove exact duplicate financial rows.
    3. Sort by original source id.
    4. Keep the highest-id record for each
       company_id + year.
    """

    dataframe = clean_year(
        dataframe
    )

    financial_columns = [
        column
        for column in dataframe.columns
        if column != "id"
    ]

    dataframe = dataframe.drop_duplicates(
        subset=financial_columns,
        keep="last"
    )

    dataframe = dataframe.sort_values(
        "id"
    )

    dataframe = dataframe.drop_duplicates(
        subset=[
            "company_id",
            "year",
        ],
        keep="last"
    )

    return dataframe.reset_index(
        drop=True
    )


def prepare_cashflow(
    dataframe
):
    return select_annual_record(
        dataframe
    )


def safe_value(
    row,
    column
):
    if row is None:
        return None

    value = row.get(
        column
    )

    if pd.isna(value):
        return None

    return value


def get_capex(
    current_balance,
    previous_balance,
    depreciation
):
    """
    Estimate CapEx.

    CapEx =
        Current Fixed Assets
        - Previous Fixed Assets
        + Depreciation
    """

    if (
        current_balance is None
        or previous_balance is None
        or depreciation is None
    ):
        return None

    return (
        current_balance
        - previous_balance
        + depreciation
    )


def prepare_period_pnl(
    dataframe
):
    """
    Validate period metadata and create one
    deterministic P&L record per financial period.

    Exact duplicate financial rows are reduced to
    one record.

    Conflicting records for the same financial
    period raise an error.
    """

    dataframe = dataframe.copy()

    required_period_columns = {
        "period_type",
        "period_months",
    }

    missing_period_columns = (
        required_period_columns
        - set(dataframe.columns)
    )

    if missing_period_columns:
        raise ValueError(
            "P&L period metadata missing: "
            f"{sorted(missing_period_columns)}"
        )

    valid_period_types = {
        "ANNUAL",
        "TTM",
        "PARTIAL",
    }

    invalid_period_types = set(
        dataframe[
            "period_type"
        ]
        .dropna()
        .unique()
    ) - valid_period_types

    if invalid_period_types:
        raise ValueError(
            "Invalid P&L period types: "
            f"{sorted(invalid_period_types)}"
        )

    period_keys = [
        "company_id",
        "year",
        "period_type",
        "period_months",
    ]

    financial_columns = [
        column
        for column in dataframe.columns
        if column != "id"
    ]

    duplicate_period_rows = dataframe[
        dataframe.duplicated(
            period_keys,
            keep=False
        )
    ].copy()

    conflict_groups = []

    if not duplicate_period_rows.empty:
        for period_key, group in (
            duplicate_period_rows.groupby(
                period_keys,
                dropna=False
            )
        ):
            comparable = (
                group[
                    financial_columns
                ]
                .reset_index(
                    drop=True
                )
            )

            if len(
                comparable.drop_duplicates()
            ) > 1:
                conflict_groups.append(
                    period_key
                )

    if conflict_groups:
        raise ValueError(
            "Conflicting P&L period duplicates: "
            f"{conflict_groups}"
        )

    dataframe = (
        dataframe
        .sort_values(
            "id"
        )
        .drop_duplicates(
            subset=period_keys,
            keep="first"
        )
        .reset_index(
            drop=True
        )
    )

    return dataframe


def build_growth_records(
    company_pnl
):
    """
    Build CAGR history from annual periods only.

    TTM and partial periods must not be mixed into
    annual CAGR calculations.
    """

    records = []

    annual_pnl = company_pnl[
        (
            company_pnl["period_type"]
            == "ANNUAL"
        )
        & company_pnl["year"].notna()
    ].copy()

    annual_pnl = (
        annual_pnl
        .sort_values(
            "year"
        )
        .reset_index(
            drop=True
        )
    )

    for _, row in annual_pnl.iterrows():
        records.append(
            {
                "year": int(
                    row["year"]
                ),
                "sales": safe_value(
                    row,
                    "sales"
                ),
                "net_profit": safe_value(
                    row,
                    "net_profit"
                ),
                "eps": safe_value(
                    row,
                    "eps"
                ),
            }
        )

    return records


def create_ratio_records(
    companies,
    pnl,
    balance,
    cashflow
):
    """
    P&L is the base financial-period timeline.

    Annual P&L records may use matching annual
    balance-sheet and cash-flow data.

    TTM and partial records use P&L-only KPIs when
    matching period-aware balance-sheet or cash-flow
    data are unavailable.

    CAGR calculations use annual P&L history only.

    IMPORTANT:
    CAGR is calculated relative to the current annual
    financial year. Therefore a 5Y CAGR on the 2021
    record uses 2016 -> 2021, while the 2022 record
    uses 2017 -> 2022.
    """

    records = []

    valid_company_ids = set(
        companies["id"]
    )

    company_sector = (
        companies
        .set_index(
            "id"
        )["broad_sector"]
        .to_dict()
    )

    pnl = pnl[
        pnl["company_id"].isin(
            valid_company_ids
        )
    ].copy()

    pnl = prepare_period_pnl(
        pnl
    )

    pnl_groups = {
        company_id: (
            group
            .sort_values(
                [
                    "year",
                    "period_type",
                    "period_months",
                ],
                na_position="last"
            )
            .reset_index(
                drop=True
            )
        )
        for company_id, group
        in pnl.groupby(
            "company_id"
        )
    }

    balance_lookup = {
        (
            row["company_id"],
            int(row["year"])
        ): row
        for _, row in balance.iterrows()
    }

    cashflow_lookup = {
        (
            row["company_id"],
            int(row["year"])
        ): row
        for _, row in cashflow.iterrows()
    }

    companies_lookup = {
        row["id"]: row
        for _, row in companies.iterrows()
    }

    for (
        company_id,
        company_pnl
    ) in pnl_groups.items():

        broad_sector = company_sector.get(
            company_id
        )

        # =====================================================
        # Build complete annual CAGR history once
        # =====================================================

        growth_records = build_growth_records(
            company_pnl
        )

        # =====================================================
        # Latest Annual Year
        # =====================================================

        annual_rows = company_pnl[
            company_pnl["period_type"] == "ANNUAL"
        ]

        if not annual_rows.empty:
            latest_annual_year = int(
                annual_rows["year"].max()
            )
        else:
            latest_annual_year = None

        for _, pnl_row in company_pnl.iterrows():

            period_type = str(
                pnl_row["period_type"]
            )

            period_months = int(
                pnl_row["period_months"]
            )

            if pd.isna(
                pnl_row["year"]
            ):
                year = None
            else:
                year = int(
                    pnl_row["year"]
                )

            # =====================================================
            # YEAR-SPECIFIC CAGR
            # =====================================================
            #
            # IMPORTANT:
            # Do NOT use one CAGR calculated from the latest
            # company year for every ratio record.
            #
            # Example:
            #   2021 record -> 2016 to 2021
            #   2022 record -> 2017 to 2022
            #
            # CAGR is only calculated for ANNUAL records.
            # TTM and PARTIAL records receive INSUFFICIENT.
            # =====================================================

            if (
                period_type == "ANNUAL"
                and year is not None
            ):
                year_growth_records = [
                    record
                    for record in growth_records
                    if record["year"] <= year
                ]

                growth = calculate_growth_cagrs(
                    year_growth_records
                )
            else:
                growth = {
                    "revenue_cagr_3y": None,
                    "revenue_cagr_3y_flag": "INSUFFICIENT",

                    "revenue_cagr_5y": None,
                    "revenue_cagr_5y_flag": "INSUFFICIENT",

                    "revenue_cagr_10y": None,
                    "revenue_cagr_10y_flag": "INSUFFICIENT",

                    "pat_cagr_3y": None,
                    "pat_cagr_3y_flag": "INSUFFICIENT",

                    "pat_cagr_5y": None,
                    "pat_cagr_5y_flag": "INSUFFICIENT",

                    "pat_cagr_10y": None,
                    "pat_cagr_10y_flag": "INSUFFICIENT",

                    "eps_cagr_3y": None,
                    "eps_cagr_3y_flag": "INSUFFICIENT",

                    "eps_cagr_5y": None,
                    "eps_cagr_5y_flag": "INSUFFICIENT",

                    "eps_cagr_10y": None,
                    "eps_cagr_10y_flag": "INSUFFICIENT",
                }

            # =====================================================
            # Annual Balance Sheet / Cash Flow
            # =====================================================

            if (
                period_type == "ANNUAL"
                and year is not None
            ):
                balance_row = (
                    balance_lookup.get(
                        (
                            company_id,
                            year,
                        )
                    )
                )

                cashflow_row = (
                    cashflow_lookup.get(
                        (
                            company_id,
                            year,
                        )
                    )
                )

                # =====================================================
                # Edge Case Logging
                # =====================================================

                if balance_row is None:
                    logging.warning(
                        f"{company_id} | {year} | Missing balance sheet"
                    )

                if cashflow_row is None:
                    logging.warning(
                        f"{company_id} | {year} | Missing cash flow"
                    )

            else:
                balance_row = None
                cashflow_row = None

            sales = safe_value(
                pnl_row,
                "sales"
            )

            operating_profit = safe_value(
                pnl_row,
                "operating_profit"
            )

            source_opm = safe_value(
                pnl_row,
                "opm_percentage"
            )

            profit_before_tax = safe_value(
                pnl_row,
                "profit_before_tax"
            )

            interest = safe_value(
                pnl_row,
                "interest"
            )

            depreciation = safe_value(
                pnl_row,
                "depreciation"
            )

            net_profit = safe_value(
                pnl_row,
                "net_profit"
            )

            eps = safe_value(
                pnl_row,
                "eps"
            )

            dividend_payout = safe_value(
                pnl_row,
                "dividend_payout"
            )

            equity_capital = safe_value(
                balance_row,
                "equity_capital"
            )

            reserves = safe_value(
                balance_row,
                "reserves"
            )

            borrowings = safe_value(
                balance_row,
                "borrowings"
            )

            total_assets = safe_value(
                balance_row,
                "total_assets"
            )

            fixed_assets = safe_value(
                balance_row,
                "fixed_assets"
            )

            if (
                profit_before_tax is None
                or interest is None
            ):
                ebit = None
            else:
                ebit = (
                    profit_before_tax
                    + interest
                )

            npm = None

            if (
                net_profit is not None
                and sales is not None
            ):
                npm = net_profit_margin(
                    net_profit,
                    sales
                )

            opm = None

            if (
                operating_profit is not None
                and sales is not None
            ):
                opm = operating_profit_margin(
                    operating_profit,
                    sales,
                    source_opm
                )

            roe = None

            if (
                net_profit is not None
                and equity_capital is not None
                and reserves is not None
            ):
                roe = return_on_equity(
                    net_profit,
                    equity_capital,
                    reserves
                )

            roce = None

            if (
                ebit is not None
                and equity_capital is not None
                and reserves is not None
                and borrowings is not None
            ):
                roce = (
                    return_on_capital_employed(
                        ebit,
                        equity_capital,
                        reserves,
                        borrowings
                    )
                )

            # =====================================================
            # Source ROE / ROCE
            # =====================================================

            company_row = companies_lookup.get(
                company_id
            )

            source_roe = safe_value(
                company_row,
                "roe_percentage"
            )

            source_roce = safe_value(
                company_row,
                "roce_percentage"
            )

            # =====================================================
            # ROE Cross Check
            # =====================================================

            if (
                period_type == "ANNUAL"
                and year == latest_annual_year
                and roe is not None
                and source_roe is not None
            ):
                difference = abs(
                    roe - source_roe
                )

                if difference > 5:
                    logging.warning(
                        f"[DATA_SOURCE] "
                        f"{company_id} | "
                        f"ROE mismatch | "
                        f"Computed={roe:.2f} | "
                        f"Source={source_roe:.2f} | "
                        f"Difference={difference:.2f}"
                    )

            # =====================================================
            # ROCE Cross Check
            # =====================================================

            if (
                period_type == "ANNUAL"
                and year == latest_annual_year
                and roce is not None
                and source_roce is not None
            ):
                difference = abs(
                    roce - source_roce
                )

                if difference > 5:
                    logging.warning(
                        f"[DATA_SOURCE] "
                        f"{company_id} | "
                        f"ROCE mismatch | "
                        f"Computed={roce:.2f} | "
                        f"Source={source_roce:.2f} | "
                        f"Difference={difference:.2f}"
                    )

            roa = None

            if (
                net_profit is not None
                and total_assets is not None
            ):
                roa = return_on_assets(
                    net_profit,
                    total_assets
                )

            de_ratio = None

            if (
                borrowings is not None
                and equity_capital is not None
                and reserves is not None
            ):
                de_ratio = debt_to_equity(
                    borrowings,
                    equity_capital,
                    reserves
                )

            leverage_flag = False

            if de_ratio is not None:
                leverage_flag = (
                    high_leverage_flag(
                        de_ratio,
                        broad_sector
                    )
                )

            icr = None

            if ebit is not None:
                icr = interest_coverage_ratio(
                    ebit,
                    interest
                )

            if interest is None:
                icr_status = "NOT_AVAILABLE"
                low_icr_flag = False
            else:
                icr_status = (
                    interest_coverage_label(
                        icr,
                        interest
                    )
                )

                low_icr_flag = (
                    low_interest_coverage_flag(
                        icr,
                        interest
                    )
                )

            turnover = None

            if (
                sales is not None
                and total_assets is not None
            ):
                turnover = asset_turnover(
                    sales,
                    total_assets
                )

            cfo = safe_value(
                cashflow_row,
                "operating_activity"
            )

            if (
                period_type == "ANNUAL"
                and year is not None
            ):
                previous_balance_row = (
                    balance_lookup.get(
                        (
                            company_id,
                            year - 1,
                        )
                    )
                )
            else:
                previous_balance_row = None

            previous_fixed_assets = safe_value(
                previous_balance_row,
                "fixed_assets"
            )

            capex = get_capex(
                fixed_assets,
                previous_fixed_assets,
                depreciation
            )

            fcf = free_cash_flow(
                cfo,
                capex
            )

            quality = cfo_quality_score(
                cfo,
                net_profit
            )

            capex_ratio = capex_intensity(
                capex,
                sales
            )

            conversion = fcf_conversion_rate(
                fcf,
                net_profit
            )

            book_value_per_share = None

            if (
                equity_capital is not None
                and reserves is not None
                and equity_capital != 0
            ):
                total_equity = (
                    equity_capital
                    + reserves
                )

                book_value_per_share = (
                    total_equity
                    / equity_capital
                )

            # =====================================================
            # Ratio Record
            # =====================================================

            record = {
                "company_id": company_id,
                "year": year,
                "period_type": period_type,
                "period_months": period_months,

                "net_profit_margin_pct": npm,
                "operating_profit_margin_pct": opm,

                "return_on_equity_pct": roe,
                "return_on_capital_employed_pct": roce,
                "return_on_assets_pct": roa,

                "debt_to_equity": de_ratio,

                "high_leverage_flag": int(
                    leverage_flag
                ),

                "interest_coverage": icr,
                "icr_label": icr_status,

                "low_interest_coverage_flag": int(
                    low_icr_flag
                ),

                "net_debt_cr": None,

                "asset_turnover": turnover,

                # =================================================
                # Revenue CAGR
                # =================================================

                "revenue_cagr_3y_pct": growth[
                    "revenue_cagr_3y"
                ],

                "revenue_cagr_3y_flag": growth[
                    "revenue_cagr_3y_flag"
                ],

                "revenue_cagr_5y_pct": growth[
                    "revenue_cagr_5y"
                ],

                "revenue_cagr_5y_flag": growth[
                    "revenue_cagr_5y_flag"
                ],

                "revenue_cagr_10y_pct": growth[
                    "revenue_cagr_10y"
                ],

                "revenue_cagr_10y_flag": growth[
                    "revenue_cagr_10y_flag"
                ],

                # =================================================
                # PAT CAGR
                # =================================================

                "pat_cagr_3y_pct": growth[
                    "pat_cagr_3y"
                ],

                "pat_cagr_3y_flag": growth[
                    "pat_cagr_3y_flag"
                ],

                "pat_cagr_5y_pct": growth[
                    "pat_cagr_5y"
                ],

                "pat_cagr_5y_flag": growth[
                    "pat_cagr_5y_flag"
                ],

                "pat_cagr_10y_pct": growth[
                    "pat_cagr_10y"
                ],

                "pat_cagr_10y_flag": growth[
                    "pat_cagr_10y_flag"
                ],

                # =================================================
                # EPS CAGR
                # =================================================

                "eps_cagr_3y_pct": growth[
                    "eps_cagr_3y"
                ],

                "eps_cagr_3y_flag": growth[
                    "eps_cagr_3y_flag"
                ],

                "eps_cagr_5y_pct": growth[
                    "eps_cagr_5y"
                ],

                "eps_cagr_5y_flag": growth[
                    "eps_cagr_5y_flag"
                ],

                "eps_cagr_10y_pct": growth[
                    "eps_cagr_10y"
                ],

                "eps_cagr_10y_flag": growth[
                    "eps_cagr_10y_flag"
                ],

                # =================================================
                # Cash Flow KPIs
                # =================================================

                "free_cash_flow_cr": fcf,

                "cfo_quality_score": (
                    quality.score
                ),

                "cfo_quality_label": (
                    quality.label
                ),

                "capex_cr": capex,

                "capex_intensity_pct": (
                    capex_ratio
                ),

                "fcf_conversion_rate_pct": (
                    conversion
                ),

                "earnings_per_share": eps,

                "book_value_per_share": (
                    book_value_per_share
                ),

                "dividend_payout_ratio_pct": (
                    dividend_payout
                ),

                "total_debt_cr": borrowings,

                "cash_from_operations_cr": cfo,
            }

            records.append(
                record
            )

    return pd.DataFrame(
        records
    )



def sync_ratio_records_to_database(ratios):
    """
    Synchronize the generated ratio records into the SQLite
    financial_ratios table.

    The CSV and SQLite database must contain the same generated
    ratio values.  In particular, this prevents stale CAGR values
    from remaining in the database after the CAGR calculation has
    been corrected.
    """

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        table_exists = cursor.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'financial_ratios'
            """
        ).fetchone()[0]

        if not table_exists:
            raise ValueError(
                "SQLite table 'financial_ratios' does not exist"
            )

        table_info = cursor.execute(
            "PRAGMA table_info(financial_ratios)"
        ).fetchall()

        db_columns = [row[1] for row in table_info]
        db_insert_columns = [
            column
            for column in db_columns
            if column != 'id' and column in ratios.columns
        ]

        if not db_insert_columns:
            raise ValueError(
                "No compatible columns found between generated ratios "
                "and financial_ratios table"
            )

        # Check required NOT NULL columns before changing the table.
        ratio_column_set = set(ratios.columns)
        missing_required = []

        for cid, name, column_type, notnull, default_value, pk in table_info:
            if name == 'id' and pk:
                # Normally an INTEGER PRIMARY KEY is auto-generated.
                continue

            if notnull and default_value is None and name not in ratio_column_set:
                missing_required.append(name)

        if missing_required:
            raise ValueError(
                "financial_ratios has required columns that are not "
                f"generated by the ratio pipeline: {missing_required}"
            )

        db_rows = ratios[db_insert_columns].copy()

        # Convert pandas NaN/NaT values to Python None for SQLite.
        db_rows = db_rows.where(pd.notna(db_rows), None)

        columns_sql = ', '.join(
            f'"{column}"'
            for column in db_insert_columns
        )
        placeholders = ', '.join(
            '?' for _ in db_insert_columns
        )

        insert_sql = (
            f'INSERT INTO financial_ratios ({columns_sql}) '
            f'VALUES ({placeholders})'
        )

        rows = [
            tuple(row)
            for row in db_rows.itertuples(
                index=False,
                name=None
            )
        ]

        connection.execute('BEGIN')
        connection.execute('DELETE FROM financial_ratios')
        cursor.executemany(insert_sql, rows)
        connection.commit()

        database_count = cursor.execute(
            'SELECT COUNT(*) FROM financial_ratios'
        ).fetchone()[0]

        if database_count != len(ratios):
            raise ValueError(
                'SQLite financial_ratios row count mismatch: '
                f'expected {len(ratios)}, got {database_count}'
            )

        print(
            'SQLite financial_ratios synchronized:',
            database_count
        )

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def validate_database_cagrs(sample_size=20, tolerance=0.1):
    """
    Validate stored 5-year revenue CAGR values directly against
    profit-and-loss history in SQLite.

    Only NORMAL CAGR cases are checked. Edge cases such as missing
    history, zero bases, or sign changes are intentionally excluded.
    """

    connection = sqlite3.connect(DB_PATH)

    try:
        query = """
        SELECT
            fr.company_id,
            fr.year,
            fr.revenue_cagr_5y_pct,
            p_old.sales AS old_sales,
            p_new.sales AS new_sales
        FROM financial_ratios fr
        JOIN profitandloss p_new
            ON p_new.company_id = fr.company_id
           AND p_new.year = fr.year
           AND p_new.period_type = 'ANNUAL'
        JOIN profitandloss p_old
            ON p_old.company_id = fr.company_id
           AND p_old.year = fr.year - 5
           AND p_old.period_type = 'ANNUAL'
        WHERE fr.period_type = 'ANNUAL'
          AND fr.revenue_cagr_5y_pct IS NOT NULL
          AND p_old.sales > 0
          AND p_new.sales >= 0
        ORDER BY fr.company_id, fr.year
        LIMIT ?
        """

        rows = connection.execute(
            query,
            (sample_size,)
        ).fetchall()

        if not rows:
            raise ValueError(
                'No eligible database CAGR rows found for validation'
            )

        failures = []

        for row in rows:
            company_id, year, stored, old_sales, new_sales = row

            calculated = (
                (new_sales / old_sales) ** (1 / 5) - 1
            ) * 100

            difference = abs(
                float(stored) - calculated
            )

            if difference > tolerance:
                failures.append(
                    (
                        company_id,
                        year,
                        float(stored),
                        calculated,
                        difference
                    )
                )

        if failures:
            first = failures[0]
            raise ValueError(
                'Database 5Y revenue CAGR validation failed. '
                f'First failure: company={first[0]}, year={first[1]}, '
                f'stored={first[2]:.4f}, calculated={first[3]:.4f}, '
                f'difference={first[4]:.4f}'
            )

        print(
            f'Database 5Y revenue CAGR validation: PASS '
            f'({len(rows)} rows checked, tolerance={tolerance} percentage points)'
        )

    finally:
        connection.close()


def save_ratio_records(
    ratios
):
    """
    Validate and persist period-aware financial ratios.

    The processed financial_ratios dataset is
    overwritten only after structural and
    financial-period checks pass.
    """

    required_columns = [
        "company_id",
        "year",
        "period_type",
        "period_months",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in ratios.columns
    ]

    if missing_columns:
        raise ValueError(
            "Ratio output metadata missing: "
            f"{missing_columns}"
        )

    if ratios.empty:
        raise ValueError(
            "Ratio output is empty"
        )

    period_keys = [
        "company_id",
        "year",
        "period_type",
        "period_months",
    ]

    duplicate_count = (
        ratios
        .duplicated(
            subset=period_keys
        )
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            "Duplicate financial periods detected "
            "before ratio persistence: "
            f"{duplicate_count}"
        )

    valid_period_types = [
        "ANNUAL",
        "TTM",
        "PARTIAL",
    ]

    invalid_period_types = ratios[
        ~ratios["period_type"].isin(
            valid_period_types
        )
    ]

    if not invalid_period_types.empty:
        invalid_values = sorted(
            invalid_period_types[
                "period_type"
            ]
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            "Invalid ratio period types detected: "
            f"{invalid_values}"
        )

    annual_invalid = ratios[
        (
            ratios["period_type"]
            == "ANNUAL"
        )
        & (
            ratios["year"].isna()
            | (
                ratios["period_months"]
                != 12
            )
        )
    ]

    if not annual_invalid.empty:
        raise ValueError(
            "Invalid ANNUAL ratio periods detected: "
            f"{len(annual_invalid)}"
        )

    ttm_invalid = ratios[
        (
            ratios["period_type"]
            == "TTM"
        )
        & (
            ratios["year"].notna()
            | (
                ratios["period_months"]
                != 12
            )
        )
    ]

    if not ttm_invalid.empty:
        raise ValueError(
            "Invalid TTM ratio periods detected: "
            f"{len(ttm_invalid)}"
        )

    partial_invalid = ratios[
        (
            ratios["period_type"]
            == "PARTIAL"
        )
        & (
            ratios["year"].isna()
            | ratios["period_months"].isna()
            | (
                ratios["period_months"]
                <= 0
            )
        )
    ]

    if not partial_invalid.empty:
        raise ValueError(
            "Invalid PARTIAL ratio periods detected: "
            f"{len(partial_invalid)}"
        )

    RATIO_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ratios.to_csv(
        RATIO_OUTPUT_PATH,
        index=False
    )

    print(
        "\nRatio records saved:",
        RATIO_OUTPUT_PATH
    )

    # Keep SQLite synchronized with the newly generated CSV.
    sync_ratio_records_to_database(ratios)

    # Fail fast if the database still contains an incorrect CAGR.
    validate_database_cagrs()

    print(
        "Saved ratio rows:",
        len(ratios)
    )


def main():

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    connection = sqlite3.connect(
        DB_PATH
    )

    try:

        companies = load_table(
            connection,
            "companies"
        )

        pnl = load_table(
            connection,
            "profitandloss"
        )

        balance = select_annual_record(
            load_table(
                connection,
                "balancesheet"
            )
        )

        cashflow = prepare_cashflow(
            load_table(
                connection,
                "cashflow"
            )
        )

        print(
            "Period-aware P&L rows:",
            len(pnl)
        )

        print(
            "Annual balance sheet rows:",
            len(balance)
        )

        print(
            "Annual cash flow rows:",
            len(cashflow)
        )

        ratios = create_ratio_records(
            companies=companies,
            pnl=pnl,
            balance=balance,
            cashflow=cashflow
        )

        duplicate_period_count = (
            ratios
            .duplicated(
                [
                    "company_id",
                    "year",
                    "period_type",
                    "period_months",
                ]
            )
            .sum()
        )

        print(
            "\nRatio records generated:",
            len(ratios)
        )

        print(
            "Companies represented:",
            ratios[
                "company_id"
            ].nunique()
        )

        print(
            "Duplicate financial periods:",
            duplicate_period_count
        )

        print(
            "\nPERIOD TYPE COUNTS"
        )

        print(
            ratios[
                "period_type"
            ].value_counts(
                dropna=False
            )
        )

        expected_companies = set(
            companies["id"]
        )

        ratio_companies = set(
            ratios["company_id"]
        )

        print(
            "Missing companies:",
            sorted(
                expected_companies
                - ratio_companies
            )
        )

        print(
            "\nNULL KPI COUNTS"
        )

        important_columns = [
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "return_on_assets_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "cfo_quality_score",
        ]

        print(
            ratios[
                important_columns
            ].isna().sum()
        )

        print(
            "\nCAGR FLAG COUNTS"
        )

        print(
            ratios[
                "revenue_cagr_5y_flag"
            ].value_counts(
                dropna=False
            )
        )

        save_ratio_records(
            ratios
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()