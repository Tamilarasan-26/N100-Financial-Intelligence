import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "src" / "etl")
)

import validator


def setup_function():
    validator.failures.clear()


def test_add_failure():
    validator.add_failure(
        "DQ-01",
        "companies",
        "CRITICAL",
        "Test failure"
    )

    assert len(validator.failures) == 1


def test_failure_rule():
    validator.add_failure(
        "DQ-01",
        "companies",
        "CRITICAL",
        "Test failure"
    )

    assert validator.failures[0]["rule"] == "DQ-01"


def test_failure_table():
    validator.add_failure(
        "DQ-02",
        "cashflow",
        "WARNING",
        "Test"
    )

    assert validator.failures[0]["table"] == "cashflow"


def test_failure_severity():
    validator.add_failure(
        "DQ-03",
        "analysis",
        "CRITICAL",
        "Test"
    )

    assert validator.failures[0]["severity"] == "CRITICAL"


def test_load_data_count():
    data = validator.load_data()

    assert len(data) == 12


def test_companies_loaded():
    data = validator.load_data()

    assert "companies" in data


def test_stock_prices_loaded():
    data = validator.load_data()

    assert "stock_prices" in data


def test_validate_detects_failures():
    data = validator.load_data()

    validator.validate(data)

    assert len(validator.failures) > 0


def test_dq03_detected():
    data = validator.load_data()

    validator.validate(data)

    rules = [
        failure["rule"]
        for failure in validator.failures
    ]

    assert "DQ-03" in rules


def test_dq12_detected():
    data = validator.load_data()

    validator.validate(data)

    rules = [
        failure["rule"]
        for failure in validator.failures
    ]

    assert "DQ-12" in rules