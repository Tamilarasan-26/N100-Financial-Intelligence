import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "src" / "etl")
)

from loader import detect_header, load_excel


RAW_DIR = Path("data/raw")


def test_analysis_header():
    assert detect_header(
        RAW_DIR / "analysis.xlsx"
    ) == 1


def test_balancesheet_header():
    assert detect_header(
        RAW_DIR / "balancesheet.xlsx"
    ) == 1


def test_financial_ratios_header():
    assert detect_header(
        RAW_DIR / "financial_ratios.xlsx"
    ) == 0


def test_market_cap_header():
    assert detect_header(
        RAW_DIR / "market_cap.xlsx"
    ) == 0


def test_analysis_row_count():
    df = load_excel(
        RAW_DIR / "analysis.xlsx"
    )

    assert len(df) == 20


def test_companies_row_count():
    df = load_excel(
        RAW_DIR / "companies.xlsx"
    )

    assert len(df) == 92


def test_stock_prices_row_count():
    df = load_excel(
        RAW_DIR / "stock_prices.xlsx"
    )

    assert len(df) == 5520


def test_company_id_normalized():
    df = load_excel(
        RAW_DIR / "cashflow.xlsx"
    )

    assert "AGTL" not in df["company_id"].values
    assert "ATGL" in df["company_id"].values


def test_year_normalized():
    df = load_excel(
        RAW_DIR / "balancesheet.xlsx"
    )

    years = df["year"].dropna()

    assert years.apply(
        lambda value: isinstance(value, int)
    ).all()


def test_columns_normalized():
    df = load_excel(
        RAW_DIR / "profitandloss.xlsx"
    )

    assert "company_id" in df.columns
    assert "net_profit" in df.columns
    assert "opm_percentage" in df.columns