from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"


@st.cache_data(ttl=600)
def run_query(query, params=None):

    conn = sqlite3.connect(DATABASE_PATH)

    if params:
        df = pd.read_sql(query, conn, params=params)
    else:
        df = pd.read_sql(query, conn)

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_companies():

    return run_query(
        """
        SELECT
            id,
            company_name
        FROM companies
        ORDER BY company_name
        """
    )

@st.cache_data(ttl=600)
def get_ratios(company_id):

    return run_query(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        params=(company_id,)
    )


@st.cache_data(ttl=600)
def get_pl(company_id):

    return run_query(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        params=(company_id,)
    )


@st.cache_data(ttl=600)
def get_bs(company_id):

    return run_query(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        params=(company_id,)
    )


@st.cache_data(ttl=600)
def get_cf(company_id):

    return run_query(
        """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        params=(company_id,)
    )


@st.cache_data(ttl=600)
def get_peers(peer_group):

    return run_query(
        """
        SELECT *
        FROM peer_groups
        WHERE peer_group_name = ?
        """,
        params=(peer_group,)
    )


@st.cache_data(ttl=600)
def get_valuation(company_id):

    return run_query(
        """
        SELECT *
        FROM market_cap
        WHERE company_id = ?
        ORDER BY year DESC
        """,
        params=(company_id,)
    )


@st.cache_data(ttl=600)
def get_sectors():

    return run_query(
        """
        SELECT DISTINCT
            broad_sector
        FROM company_master
        ORDER BY broad_sector
        """
    )
    
@st.cache_data(ttl=600)
def get_home_kpis(year):

    return run_query(
        """
        SELECT
            AVG(return_on_equity_pct) AS avg_roe,
            AVG(pe_ratio) AS avg_pe,
            AVG(debt_to_equity) AS avg_de,
            AVG(revenue_cagr_5y_pct) AS avg_revenue_cagr,
            SUM(
                CASE
                    WHEN debt_to_equity = 0 THEN 1
                    ELSE 0
                END
            ) AS debt_free_companies
        FROM financial_ratios fr
        LEFT JOIN market_cap mc
            ON fr.company_id = mc.company_id
            AND fr.year = mc.year
        WHERE fr.year = ?
        """,
        params=(year,)
    )
    

@st.cache_data(ttl=600)
def get_sector_distribution():

    return run_query(
        """
        SELECT
            broad_sector,
            COUNT(*) AS company_count
        FROM companies
        GROUP BY broad_sector
        ORDER BY company_count DESC
        """
    )
    
@st.cache_data(ttl=600)
def get_top_companies(year):

    return run_query(
        """
        SELECT
            c.company_name,
            fr.composite_quality_score
        FROM financial_ratios fr
        JOIN companies c
            ON fr.company_id = c.id
        WHERE fr.year = ?
        ORDER BY fr.composite_quality_score DESC
        LIMIT 5
        """,
        params=(year,)
    )
    
@st.cache_data(ttl=600)
def get_company_info(company_id):

    return run_query(
        """
        SELECT
            id,
            company_name,
            broad_sector,
            sub_sector,
            website,
            about_company
        FROM companies
        WHERE id = ?
        """,
        params=(company_id,)
    )
    
@st.cache_data(ttl=600)
def get_company_insights(company_id):

    return run_query(
        """
        SELECT
            pros,
            cons
        FROM company_insights
        WHERE company_id = ?
        """,
        params=(company_id,)
    )
    
@st.cache_data(ttl=600)
def get_screener_data():

    return run_query("""
    SELECT
        c.id,
        c.company_name,
        c.broad_sector,
        c.sub_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.revenue_cagr_5y_pct,
        fr.pat_cagr_5y_pct,
        fr.operating_profit_margin_pct,
        fr.interest_coverage,
        fr.composite_quality_score,

        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct

    FROM companies c

    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id

    LEFT JOIN market_cap mc
        ON c.id = mc.company_id
        AND fr.year = mc.year

    WHERE fr.year = 2024

    ORDER BY c.company_name
    """)
    
@st.cache_data(ttl=600)
def get_peer_groups():

    return run_query("""
    SELECT DISTINCT
        peer_group_name
    FROM peer_groups
    ORDER BY peer_group_name
    """)
    
@st.cache_data(ttl=600)
def get_peer_companies(group):

    return run_query("""
    SELECT *
    FROM peer_groups
    WHERE peer_group_name = ?
    """, params=(group,))
    
@st.cache_data(ttl=600)
def get_peer_groups():

    return run_query("""
        SELECT DISTINCT
            broad_sector
        FROM companies
        ORDER BY broad_sector
    """)

@st.cache_data(ttl=600)
def get_peer_companies(sector):

    return run_query(
        """
        SELECT
            c.id,
            c.company_name,
            c.broad_sector,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.revenue_cagr_5y_pct,
            fr.interest_coverage,
            fr.composite_quality_score,

            mc.pe_ratio,
            mc.pb_ratio

        FROM companies c

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id

        LEFT JOIN market_cap mc
            ON c.id = mc.company_id
            AND fr.year = mc.year

        WHERE
            c.broad_sector = ?
            AND fr.year = 2024

        ORDER BY c.company_name
        """,
        params=(sector,)
    )
    
@st.cache_data(ttl=600)
def get_trend_data(company_id):

    return run_query(
        """
        SELECT
            year,
            return_on_equity_pct,
            return_on_capital_employed_pct,
            net_profit_margin_pct,
            debt_to_equity,
            revenue_cagr_5y_pct,
            pat_cagr_5y_pct,
            interest_coverage,
            free_cash_flow_cr,
            composite_quality_score
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year
        """,
        params=(company_id,)
    )
    
@st.cache_data(ttl=600)
def get_sector_data():

    return run_query(
        """
        SELECT
            c.company_name,
            c.broad_sector,
            c.sub_sector,

            pl.sales,

            fr.return_on_equity_pct,

            mc.market_cap_crore

        FROM companies c

        LEFT JOIN profitandloss pl
            ON c.id = pl.company_id

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
            AND fr.year = pl.year

        LEFT JOIN market_cap mc
            ON c.id = mc.company_id
            AND mc.year = pl.year

        WHERE
            pl.year = 2024

        ORDER BY
            c.company_name
        """
    )
    
@st.cache_data(ttl=600)
def get_sector_kpis(sector):

    return run_query(
        """
        SELECT
            broad_sector,
            AVG(return_on_equity_pct) AS avg_roe,
            AVG(return_on_capital_employed_pct) AS avg_roce,
            AVG(net_profit_margin_pct) AS avg_margin,
            AVG(debt_to_equity) AS avg_de,
            AVG(revenue_cagr_5y_pct) AS avg_growth

        FROM companies c

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id

        WHERE
            broad_sector = ?
            AND fr.year = 2024

        GROUP BY broad_sector
        """,
        params=(sector,)
    )
    
@st.cache_data(ttl=600)
def get_capital_data():

    return run_query(
        """
        SELECT

            c.id,
            c.company_name,
            c.broad_sector,

            ca.capital_allocation_pattern,

            mc.market_cap_crore,

            ca.operating_activity,
            ca.investing_activity,
            ca.financing_activity,
            ca.net_cash_flow

        FROM capital_allocation ca

        LEFT JOIN companies c
            ON ca.company_id = c.id

        LEFT JOIN market_cap mc
            ON ca.company_id = mc.company_id
            AND ca.year = mc.year

        WHERE
            ca.year = 2024

        ORDER BY
            capital_allocation_pattern,
            company_name
        """
    )
    
@st.cache_data(ttl=600)
def get_annual_reports(company_id):

    return run_query(
        """
        SELECT
            year,
            annual_report
        FROM documents

        WHERE company_id = ?

        ORDER BY year DESC
        """,
        params=(company_id,)
    )