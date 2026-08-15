import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src" / "etl")
)

import validator


# ============================================================
# BASE DATA
# ============================================================

def base_data():

    return {
        "companies": pd.DataFrame({
            "id": ["TCS"]
        }),

        "balancesheet": pd.DataFrame({
            "total_assets": [1000]
        }),

        "profitandloss": pd.DataFrame({
            "sales": [1000],
            "net_profit": [100]
        }),

        "stock_prices": pd.DataFrame({
            "date": ["2024-01-01"],
            "close_price": [100],
            "high_price": [110],
            "low_price": [90],
            "volume": [1000]
        }),

        "financial_ratios": pd.DataFrame({
            "debt_to_equity": [1.0],
            "interest_coverage": [2.0]
        }),

        "market_cap": pd.DataFrame({
            "market_cap_crore": [100000],
            "pe_ratio": [20]
        }),

        "sectors": pd.DataFrame({
            "company_id": ["TCS"],
            "broad_sector": ["Information Technology"]
        }),
    }


# ============================================================
# HELPER
# ============================================================

def run_validation(data):

    validator.failures.clear()

    validator.validate(data)

    return validator.failures


def get_failure(rule_id):

    for failure in validator.failures:

        if failure["rule"] == rule_id:
            return failure

    return None


# ============================================================
# DQ-01
# Duplicate company IDs
# ============================================================

def test_dq01_duplicate_company_ids():

    data = base_data()

    data["companies"] = pd.DataFrame({
        "id": ["TCS", "TCS"]
    })

    run_validation(data)

    failure = get_failure("DQ-01")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-02
# Null company_id
# ============================================================

def test_dq02_null_company_id():

    data = base_data()

    data["cashflow"] = pd.DataFrame({
        "company_id": [None]
    })

    run_validation(data)

    failure = get_failure("DQ-02")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-03
# Invalid foreign key
# ============================================================

def test_dq03_invalid_foreign_key():

    data = base_data()

    data["cashflow"] = pd.DataFrame({
        "company_id": ["INVALID"]
    })

    run_validation(data)

    failure = get_failure("DQ-03")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-04
# Negative total assets
# ============================================================

def test_dq04_negative_total_assets():

    data = base_data()

    data["balancesheet"] = pd.DataFrame({
        "total_assets": [-100]
    })

    run_validation(data)

    failure = get_failure("DQ-04")

    assert failure is not None
    assert failure["severity"] == "WARNING"


# ============================================================
# DQ-05
# Non-positive sales
# ============================================================

def test_dq05_non_positive_sales():

    data = base_data()

    data["profitandloss"] = pd.DataFrame({
        "sales": [0],
        "net_profit": [100]
    })

    run_validation(data)

    failure = get_failure("DQ-05")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-06
# Missing net profit
# ============================================================

def test_dq06_missing_net_profit():

    data = base_data()

    data["profitandloss"] = pd.DataFrame({
        "sales": [1000],
        "net_profit": [None]
    })

    run_validation(data)

    failure = get_failure("DQ-06")

    assert failure is not None
    assert failure["severity"] == "WARNING"


# ============================================================
# DQ-07
# Missing stock date
# ============================================================

def test_dq07_missing_stock_date():

    data = base_data()

    data["stock_prices"] = pd.DataFrame({
        "date": [None],
        "close_price": [100],
        "high_price": [110],
        "low_price": [90],
        "volume": [1000]
    })

    run_validation(data)

    failure = get_failure("DQ-07")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-08
# Invalid closing price
# ============================================================

def test_dq08_invalid_closing_price():

    data = base_data()

    data["stock_prices"] = pd.DataFrame({
        "date": ["2024-01-01"],
        "close_price": [0],
        "high_price": [110],
        "low_price": [90],
        "volume": [1000]
    })

    run_validation(data)

    failure = get_failure("DQ-08")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-09
# High price lower than low price
# ============================================================

def test_dq09_high_price_lower_than_low_price():

    data = base_data()

    data["stock_prices"] = pd.DataFrame({
        "date": ["2024-01-01"],
        "close_price": [100],
        "high_price": [80],
        "low_price": [90],
        "volume": [1000]
    })

    run_validation(data)

    failure = get_failure("DQ-09")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-10
# Negative stock volume
# ============================================================

def test_dq10_negative_stock_volume():

    data = base_data()

    data["stock_prices"] = pd.DataFrame({
        "date": ["2024-01-01"],
        "close_price": [100],
        "high_price": [110],
        "low_price": [90],
        "volume": [-100]
    })

    run_validation(data)

    failure = get_failure("DQ-10")

    assert failure is not None
    assert failure["severity"] == "WARNING"


# ============================================================
# DQ-11
# Missing debt-to-equity
# ============================================================

def test_dq11_missing_debt_to_equity():

    data = base_data()

    data["financial_ratios"] = pd.DataFrame({
        "debt_to_equity": [None],
        "interest_coverage": [2.0]
    })

    run_validation(data)

    failure = get_failure("DQ-11")

    assert failure is not None
    assert failure["severity"] == "WARNING"


# ============================================================
# DQ-12
# Negative interest coverage
# ============================================================

def test_dq12_negative_interest_coverage():

    data = base_data()

    data["financial_ratios"] = pd.DataFrame({
        "debt_to_equity": [1.0],
        "interest_coverage": [-1.0]
    })

    run_validation(data)

    failure = get_failure("DQ-12")

    assert failure is not None
    assert failure["severity"] == "WARNING"


# ============================================================
# DQ-13
# Invalid market capitalization
# ============================================================

def test_dq13_invalid_market_cap():

    data = base_data()

    data["market_cap"] = pd.DataFrame({
        "market_cap_crore": [0],
        "pe_ratio": [20]
    })

    run_validation(data)

    failure = get_failure("DQ-13")

    assert failure is not None
    assert failure["severity"] == "CRITICAL"


# ============================================================
# DQ-14
# Negative PE ratio
# ============================================================

def test_dq14_negative_pe_ratio():

    data = base_data()

    data["market_cap"] = pd.DataFrame({
        "market_cap_crore": [100000],
        "pe_ratio": [-5]
    })

    run_validation(data)

    failure = get_failure("DQ-14")

    assert failure is not None
    assert failure["severity"] == "WARNING"