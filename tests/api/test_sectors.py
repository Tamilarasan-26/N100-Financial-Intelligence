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
# GET ALL SECTORS
# ============================================================

def test_get_sectors_returns_200():

    response = client.get(
        "/api/v1/sectors"
    )

    assert response.status_code == 200


def test_get_sectors_response_structure():

    response = client.get(
        "/api/v1/sectors"
    )

    data = response.json()

    assert "count" in data
    assert "sectors" in data

    assert isinstance(
        data["count"],
        int
    )

    assert isinstance(
        data["sectors"],
        list
    )


def test_get_sectors_contains_expected_fields():

    response = client.get(
        "/api/v1/sectors"
    )

    data = response.json()

    assert data["count"] > 0

    sector = data["sectors"][0]

    expected_fields = {
        "sector",
        "company_count",
        "median_roe",
        "median_pe",
        "median_de",
    }

    assert expected_fields.issubset(
        set(sector.keys())
    )


def test_get_sectors_contains_information_technology():

    response = client.get(
        "/api/v1/sectors"
    )

    data = response.json()

    sector_names = [
        sector["sector"]
        for sector in data["sectors"]
    ]

    assert "Information Technology" in sector_names


def test_get_sectors_company_counts_are_valid():

    response = client.get(
        "/api/v1/sectors"
    )

    data = response.json()

    for sector in data["sectors"]:

        assert isinstance(
            sector["company_count"],
            int
        )

        assert sector["company_count"] > 0


# ============================================================
# GET COMPANIES BY SECTOR
# ============================================================

def test_get_it_companies_returns_200():

    response = client.get(
        "/api/v1/sectors/Information%20Technology/companies"
    )

    assert response.status_code == 200


def test_get_sector_companies_response_structure():

    response = client.get(
        "/api/v1/sectors/Information%20Technology/companies"
    )

    data = response.json()

    assert data["sector"] == "Information Technology"

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


def test_get_sector_companies_contains_expected_fields():

    response = client.get(
        "/api/v1/sectors/Information%20Technology/companies"
    )

    data = response.json()

    assert data["count"] > 0

    company = data["companies"][0]

    expected_fields = {
        "id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "year",
        "roe_pct",
        "debt_to_equity",
        "revenue_cagr_5y_pct",
        "pat_cagr_5y_pct",
        "free_cash_flow_cr",
        "composite_quality_score",
    }

    assert expected_fields.issubset(
        set(company.keys())
    )


def test_sector_companies_have_correct_sector():

    response = client.get(
        "/api/v1/sectors/Information%20Technology/companies"
    )

    data = response.json()

    for company in data["companies"]:

        assert (
            company["broad_sector"]
            == "Information Technology"
        )


# ============================================================
# INVALID SECTOR
# ============================================================

def test_invalid_sector_returns_404():

    response = client.get(
        "/api/v1/sectors/InvalidSector/companies"
    )

    assert response.status_code == 404


def test_invalid_sector_contains_error_message():

    response = client.get(
        "/api/v1/sectors/InvalidSector/companies"
    )

    data = response.json()

    assert "detail" in data

    assert (
        "not found"
        in data["detail"].lower()
    )