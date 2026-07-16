import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    low_interest_coverage_flag,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity_normal_case():
    result = debt_to_equity(
        total_debt=50,
        equity_capital=40,
        reserves=60
    )

    assert result == pytest.approx(0.5)


def test_debt_free_company_returns_zero():
    result = debt_to_equity(
        total_debt=0,
        equity_capital=40,
        reserves=60
    )

    assert result == 0


def test_high_leverage_flag_normal_sector():
    result = high_leverage_flag(
        debt_equity=2.5,
        broad_sector="Industrials"
    )

    assert result is True


def test_financials_high_leverage_carve_out():
    result = high_leverage_flag(
        debt_equity=5.0,
        broad_sector="Financials"
    )

    assert result is False


def test_zero_interest_returns_none_and_debt_free():
    ratio = interest_coverage_ratio(
        ebit=30,
        interest=0
    )

    label = interest_coverage_label(
        interest_coverage=ratio,
        interest=0
    )

    assert ratio is None
    assert label == "Debt Free"


def test_low_interest_coverage_warning_flag():
    ratio = interest_coverage_ratio(
        ebit=10,
        interest=10
    )

    result = low_interest_coverage_flag(
        interest_coverage=ratio,
        interest=10
    )

    assert result is True


def test_net_debt_normal_case():
    result = net_debt(
        total_debt=100,
        cash_and_equivalents=25
    )

    assert result == pytest.approx(75)


def test_asset_turnover_zero_assets():
    result = asset_turnover(
        sales=200,
        total_assets=0
    )

    assert result is None