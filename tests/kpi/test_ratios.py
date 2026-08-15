import logging
import sys
from pathlib import Path

import pytest


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
    is_roce_above_benchmark,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    low_interest_coverage_flag,
    net_debt,
    asset_turnover,
)


# ============================================================
# NET PROFIT MARGIN
# ============================================================

def test_net_profit_margin_normal_case():

    result = net_profit_margin(
        net_profit=20,
        sales=100
    )

    assert result == pytest.approx(20.0)


def test_net_profit_margin_zero_sales():

    result = net_profit_margin(
        net_profit=20,
        sales=0
    )

    assert result is None


# ============================================================
# OPERATING PROFIT MARGIN
# ============================================================

def test_operating_profit_margin_normal_case():

    result = operating_profit_margin(
        operating_profit=25,
        sales=100,
        source_opm=25
    )

    assert result == pytest.approx(25.0)


def test_operating_profit_margin_cross_check_mismatch(
    caplog
):

    with caplog.at_level(logging.WARNING):

        result = operating_profit_margin(
            operating_profit=25,
            sales=100,
            source_opm=20
        )

    assert result == pytest.approx(25.0)

    assert (
        "OPM cross-check mismatch"
        in caplog.text
    )


def test_operating_profit_margin_skips_invalid_source_opm(
    caplog
):

    with caplog.at_level(logging.WARNING):

        result = operating_profit_margin(
            operating_profit=25,
            sales=100,
            source_opm=1353
        )

    assert result == pytest.approx(25.0)

    assert (
        "OPM cross-check mismatch"
        not in caplog.text
    )


# ============================================================
# RETURN ON EQUITY
# ============================================================

def test_return_on_equity_normal_case():

    result = return_on_equity(
        net_profit=20,
        equity_capital=40,
        reserves=60
    )

    assert result == pytest.approx(20.0)


def test_return_on_equity_negative_equity():

    result = return_on_equity(
        net_profit=20,
        equity_capital=40,
        reserves=-50
    )

    assert result is None


# ============================================================
# RETURN ON CAPITAL EMPLOYED
# ============================================================

def test_return_on_capital_employed_normal_case():

    result = return_on_capital_employed(
        ebit=30,
        equity_capital=40,
        reserves=60,
        borrowings=50
    )

    assert result == pytest.approx(20.0)


# ============================================================
# RETURN ON ASSETS
# ============================================================

def test_return_on_assets_zero_assets():

    result = return_on_assets(
        net_profit=20,
        total_assets=0
    )

    assert result is None


# ============================================================
# ROCE BENCHMARK
# ============================================================

def test_roce_non_financial_above_threshold():

    result = is_roce_above_benchmark(
        roce=20,
        broad_sector="Information Technology"
    )

    assert result is True


def test_roce_financial_sector_above_benchmark():

    result = is_roce_above_benchmark(
        roce=18,
        broad_sector="Financials",
        sector_benchmark=15
    )

    assert result is True


# ============================================================
# DEBT TO EQUITY
# ============================================================

def test_debt_to_equity_normal_case():

    result = debt_to_equity(
        total_debt=50,
        equity_capital=50,
        reserves=50
    )

    assert result == pytest.approx(0.5)


def test_debt_to_equity_debt_free_company():

    result = debt_to_equity(
        total_debt=0,
        equity_capital=50,
        reserves=50
    )

    assert result == 0


def test_debt_to_equity_negative_equity():

    result = debt_to_equity(
        total_debt=50,
        equity_capital=50,
        reserves=-60
    )

    assert result is None


# ============================================================
# HIGH LEVERAGE FLAG
# ============================================================

def test_high_leverage_flag_above_threshold():

    result = high_leverage_flag(
        debt_equity=3,
        broad_sector="Industrials",
        threshold=2
    )

    assert result is True


# ============================================================
# INTEREST COVERAGE
# ============================================================

def test_interest_coverage_normal_case():

    result = interest_coverage_ratio(
        ebit=100,
        interest=20
    )

    assert result == pytest.approx(5.0)


def test_interest_coverage_zero_interest():

    result = interest_coverage_ratio(
        ebit=100,
        interest=0
    )

    assert result is None


# ============================================================
# INTEREST COVERAGE LABEL
# ============================================================

def test_interest_coverage_debt_free_label():

    result = interest_coverage_label(
        interest_coverage=None,
        interest=0
    )

    assert result == "Debt Free"


# ============================================================
# LOW INTEREST COVERAGE FLAG
# ============================================================

def test_low_interest_coverage_flag():

    result = low_interest_coverage_flag(
        interest_coverage=1.0,
        interest=10
    )

    assert result is True


# ============================================================
# NET DEBT
# ============================================================

def test_net_debt_normal_case():

    result = net_debt(
        total_debt=100,
        cash_and_equivalents=30
    )

    assert result == pytest.approx(70)


# ============================================================
# ASSET TURNOVER
# ============================================================

def test_asset_turnover_normal_case():

    result = asset_turnover(
        sales=200,
        total_assets=100
    )

    assert result == pytest.approx(2.0)