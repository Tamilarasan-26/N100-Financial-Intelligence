import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "src" / "etl")
)

from normaliser import (
    normalize_year,
    normalize_ticker,
    normalize_columns,
)


def test_year_dec_2012():
    assert normalize_year("Dec 2012") == 2012


def test_year_mar_2014():
    assert normalize_year("Mar 2014") == 2014


def test_integer_year():
    assert normalize_year(2020) == 2020


def test_string_year():
    assert normalize_year("2021") == 2021


def test_missing_year():
    assert normalize_year(None) is None


def test_invalid_year():
    assert normalize_year("invalid") is None


def test_empty_year():
    assert normalize_year("") is None


def test_ticker_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_ticker_spaces():
    assert normalize_ticker("  infy  ") == "INFY"


def test_ticker_ns_suffix():
    assert normalize_ticker("TCS.NS") == "TCS"


def test_ticker_bo_suffix():
    assert normalize_ticker("INFY.BO") == "INFY"


def test_agtl_mapping():
    assert normalize_ticker("AGTL") == "ATGL"


def test_agtl_lowercase_mapping():
    assert normalize_ticker("agtl") == "ATGL"


def test_missing_ticker():
    assert normalize_ticker(None) is None


def test_ticker_internal_spaces():
    assert normalize_ticker("HDFC BANK") == "HDFCBANK"


def test_column_lowercase():
    df = pd.DataFrame(columns=["Company ID"])

    result = normalize_columns(df)

    assert "company_id" in result.columns


def test_column_ampersand():
    df = pd.DataFrame(columns=["Profit & Loss"])

    result = normalize_columns(df)

    assert "profit_and_loss" in result.columns


def test_column_percentage():
    df = pd.DataFrame(columns=["ROE %"])

    result = normalize_columns(df)

    assert "roe_pct" in result.columns


def test_multiple_columns():
    df = pd.DataFrame(
        columns=[
            "Company ID",
            "Net Profit",
            "ROE %"
        ]
    )

    result = normalize_columns(df)

    assert result.columns.tolist() == [
        "company_id",
        "net_profit",
        "roe_pct"
    ]