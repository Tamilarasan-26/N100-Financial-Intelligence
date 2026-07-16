import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.analytics.cagr import (
    NORMAL,
    DECLINE_TO_LOSS,
    TURNAROUND,
    BOTH_NEGATIVE,
    ZERO_BASE,
    INSUFFICIENT,
    calculate_cagr,
    calculate_period_cagr,
    calculate_growth_cagrs,
)


def test_normal_positive_cagr():
    result = calculate_cagr(
        start_value=100,
        end_value=200,
        years=5
    )

    assert result.value == pytest.approx(
        14.869835499703509
    )

    assert result.flag == NORMAL


def test_decline_to_loss():
    result = calculate_cagr(
        start_value=100,
        end_value=-20,
        years=5
    )

    assert result.value is None
    assert result.flag == DECLINE_TO_LOSS


def test_turnaround():
    result = calculate_cagr(
        start_value=-100,
        end_value=20,
        years=5
    )

    assert result.value is None
    assert result.flag == TURNAROUND


def test_both_negative():
    result = calculate_cagr(
        start_value=-100,
        end_value=-20,
        years=5
    )

    assert result.value is None
    assert result.flag == BOTH_NEGATIVE


def test_zero_base():
    result = calculate_cagr(
        start_value=0,
        end_value=100,
        years=5
    )

    assert result.value is None
    assert result.flag == ZERO_BASE


def test_insufficient_invalid_years():
    result = calculate_cagr(
        start_value=100,
        end_value=200,
        years=0
    )

    assert result.value is None
    assert result.flag == INSUFFICIENT


def test_period_cagr_insufficient_years():
    records = [
        {
            "year": 2020,
            "sales": 100
        },
        {
            "year": 2024,
            "sales": 200
        }
    ]

    result = calculate_period_cagr(
        records=records,
        value_column="sales",
        period_years=5
    )

    assert result.value is None
    assert result.flag == INSUFFICIENT


def test_revenue_cagr_3_years():
    records = [
        {
            "year": 2020,
            "sales": 100
        },
        {
            "year": 2023,
            "sales": 133.1
        }
    ]

    result = calculate_period_cagr(
        records=records,
        value_column="sales",
        period_years=3
    )

    assert result.value == pytest.approx(
        10.0
    )

    assert result.flag == NORMAL


def test_pat_cagr_5_years():
    records = [
        {
            "year": 2019,
            "net_profit": 100
        },
        {
            "year": 2024,
            "net_profit": 161.051
        }
    ]

    result = calculate_period_cagr(
        records=records,
        value_column="net_profit",
        period_years=5
    )

    assert result.value == pytest.approx(
        10.0
    )

    assert result.flag == NORMAL


def test_growth_cagrs_returns_value_and_flag():
    records = [
        {
            "year": 2014,
            "sales": 100,
            "net_profit": 50,
            "eps": 5
        },
        {
            "year": 2019,
            "sales": 150,
            "net_profit": 75,
            "eps": 7.5
        },
        {
            "year": 2021,
            "sales": 170,
            "net_profit": 85,
            "eps": 8.5
        },
        {
            "year": 2024,
            "sales": 200,
            "net_profit": 100,
            "eps": 10
        }
    ]

    results = calculate_growth_cagrs(
        records
    )

    assert "revenue_cagr_3y" in results

    assert (
        "revenue_cagr_3y_flag"
        in results
    )

    assert "pat_cagr_5y" in results

    assert "pat_cagr_5y_flag" in results

    assert "eps_cagr_10y" in results

    assert "eps_cagr_10y_flag" in results

    assert (
        results["revenue_cagr_3y_flag"]
        == NORMAL
    )

    assert (
        results["pat_cagr_5y_flag"]
        == NORMAL
    )

    assert (
        results["eps_cagr_10y_flag"]
        == NORMAL
    )