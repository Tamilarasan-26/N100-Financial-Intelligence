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
)


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


def test_return_on_capital_employed_normal_case():
    result = return_on_capital_employed(
        ebit=30,
        equity_capital=40,
        reserves=60,
        borrowings=50
    )

    assert result == pytest.approx(20.0)


def test_return_on_assets_zero_assets():
    result = return_on_assets(
        net_profit=20,
        total_assets=0
    )

    assert result is None