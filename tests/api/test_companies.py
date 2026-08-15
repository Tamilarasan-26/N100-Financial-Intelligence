import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.api.main import app


client = TestClient(app)


# ============================================================
# GET ALL COMPANIES
# ============================================================

def test_get_all_companies_returns_200():

    response = client.get(
        "/api/v1/companies"
    )

    assert response.status_code == 200


def test_get_all_companies_has_expected_structure():

    response = client.get(
        "/api/v1/companies"
    )

    data = response.json()

    assert "count" in data
    assert "companies" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["companies"],
        list
    )


def test_get_all_companies_contains_tcs():

    response = client.get(
        "/api/v1/companies"
    )

    data = response.json()

    company_ids = [
        company["id"]
        for company in data["companies"]
    ]

    assert "TCS" in company_ids


# ============================================================
# GET TCS COMPANY PROFILE
# ============================================================

def test_get_tcs_profile_returns_200():

    response = client.get(
        "/api/v1/companies/TCS"
    )

    assert response.status_code == 200


def test_get_tcs_profile_structure():

    response = client.get(
        "/api/v1/companies/TCS"
    )

    data = response.json()

    assert "company" in data
    assert "latest_ratios" in data

    assert data["company"]["id"] == "TCS"


def test_get_tcs_profile_contains_company_name():

    response = client.get(
        "/api/v1/companies/TCS"
    )

    data = response.json()

    company = data["company"]

    assert company["company_name"] is not None
    assert len(company["company_name"]) > 0


# ============================================================
# INVALID COMPANY
# ============================================================

def test_invalid_company_returns_404():

    response = client.get(
        "/api/v1/companies/INVALID_COMPANY"
    )

    assert response.status_code == 404


def test_invalid_company_error_message():

    response = client.get(
        "/api/v1/companies/INVALID_COMPANY"
    )

    data = response.json()

    assert "detail" in data

    assert (
        "not found"
        in data["detail"].lower()
    )


# ============================================================
# COMPANY FILTER
# ============================================================

def test_company_search_tcs():

    response = client.get(
        "/api/v1/companies",
        params={
            "search": "TCS"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1


# ============================================================
# COMPANY PROFILE RATIOS
# ============================================================

def test_tcs_latest_ratios_present():

    response = client.get(
        "/api/v1/companies/TCS"
    )

    data = response.json()

    assert data["latest_ratios"] is not None


def test_tcs_latest_ratios_contains_year():

    response = client.get(
        "/api/v1/companies/TCS"
    )

    data = response.json()

    ratios = data["latest_ratios"]

    assert "year" in ratios