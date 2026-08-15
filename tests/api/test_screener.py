import sys
from pathlib import Path

from fastapi.testclient import TestClient


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.api.main import app


client = TestClient(app)


# ============================================================
# BASIC SCREENER
# ============================================================

def test_screener_returns_200():

    response = client.get(
        "/api/v1/screener"
    )

    assert response.status_code == 200


def test_screener_response_structure():

    response = client.get(
        "/api/v1/screener"
    )

    data = response.json()

    assert "count" in data
    assert "filters" in data
    assert "companies" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["companies"],
        list
    )


def test_screener_filters_structure():

    response = client.get(
        "/api/v1/screener"
    )

    data = response.json()

    filters = data["filters"]

    expected_filters = {
        "min_roe",
        "max_de",
        "min_fcf",
        "sector",
        "min_rev_cagr_5yr",
        "min_pat_cagr_5yr",
        "max_pe",
    }

    assert expected_filters.issubset(
        set(filters.keys())
    )


# ============================================================
# ROE FILTER
# ============================================================

def test_screener_min_roe_filter():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_roe": 10
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["min_roe"] == 10

    for company in data["companies"]:

        if company["roe_pct"] is not None:

            assert company["roe_pct"] >= 10


# ============================================================
# DEBT TO EQUITY FILTER
# ============================================================

def test_screener_max_de_filter():

    response = client.get(
        "/api/v1/screener",
        params={
            "max_de": 2
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["max_de"] == 2

    for company in data["companies"]:

        if company["debt_to_equity"] is not None:

            assert company["debt_to_equity"] <= 2


# ============================================================
# SECTOR FILTER
# ============================================================

def test_screener_sector_filter():

    response = client.get(
        "/api/v1/screener",
        params={
            "sector": "Information Technology"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["filters"]["sector"]
        == "Information Technology"
    )

    for company in data["companies"]:

        assert (
            company["broad_sector"]
            == "Information Technology"
        )


# ============================================================
# FREE CASH FLOW FILTER
# ============================================================

def test_screener_min_fcf_filter():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_fcf": 100
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["min_fcf"] == 100

    for company in data["companies"]:

        if company["free_cash_flow_cr"] is not None:

            assert (
                company["free_cash_flow_cr"]
                >= 100
            )


# ============================================================
# P/E FILTER
# ============================================================

def test_screener_max_pe_filter():

    response = client.get(
        "/api/v1/screener",
        params={
            "max_pe": 50
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filters"]["max_pe"] == 50

    for company in data["companies"]:

        if company["pe_ratio"] is not None:

            assert company["pe_ratio"] <= 50


# ============================================================
# INVALID ROE
# ============================================================

def test_screener_negative_roe_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_roe": -10
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert (
        "min_roe cannot be negative"
        in data["detail"]
    )


# ============================================================
# INVALID DEBT TO EQUITY
# ============================================================

def test_screener_negative_de_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "max_de": -1
        }
    )

    assert response.status_code == 400


# ============================================================
# INVALID FCF
# ============================================================

def test_screener_negative_fcf_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_fcf": -100
        }
    )

    assert response.status_code == 400


# ============================================================
# INVALID PE
# ============================================================

def test_screener_negative_pe_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "max_pe": -5
        }
    )

    assert response.status_code == 400


# ============================================================
# INVALID REVENUE CAGR
# ============================================================

def test_screener_invalid_revenue_cagr_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_rev_cagr_5yr": -101
        }
    )

    assert response.status_code == 400


# ============================================================
# INVALID PAT CAGR
# ============================================================

def test_screener_invalid_pat_cagr_returns_400():

    response = client.get(
        "/api/v1/screener",
        params={
            "min_pat_cagr_5yr": -101
        }
    )

    assert response.status_code == 400