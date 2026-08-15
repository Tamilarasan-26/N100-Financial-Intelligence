import sys
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.api.main import app, DB_PATH


client = TestClient(app)


def get_valid_peer_group():
    """
    Get one valid peer group directly from the test database.
    """

    connection = sqlite3.connect(DB_PATH)

    try:
        row = connection.execute(
            """
            SELECT peer_group_name
            FROM peer_groups
            LIMIT 1
            """
        ).fetchone()

        return row[0]

    finally:
        connection.close()


def test_peer_group_returns_200():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    assert response.status_code == 200


def test_peer_group_response_structure():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    assert "peer_group" in data
    assert "year" in data
    assert "count" in data
    assert "companies" in data


def test_peer_group_name_is_correct():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    assert data["peer_group"] == group


def test_peer_group_count_matches_companies():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    assert data["count"] == len(
        data["companies"]
    )


def test_peer_company_structure():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    assert data["count"] > 0

    company = data["companies"][0]

    assert "company_id" in company
    assert "company_name" in company
    assert "broad_sector" in company
    assert "sub_sector" in company
    assert "market_cap_category" in company
    assert "is_benchmark" in company
    assert "metrics" in company


def test_peer_metrics_structure():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    company = data["companies"][0]

    metrics = company["metrics"]

    if metrics:

        metric_name = next(
            iter(metrics)
        )

        metric = metrics[metric_name]

        assert "value" in metric
        assert "percentile_rank" in metric


def test_peer_group_has_benchmark_flag():
    group = get_valid_peer_group()

    response = client.get(
        f"/api/v1/peers/{group}"
    )

    data = response.json()

    benchmark_companies = [
        company
        for company in data["companies"]
        if company["is_benchmark"] is True
    ]

    assert len(benchmark_companies) >= 1


def test_invalid_peer_group_returns_404():

    response = client.get(
        "/api/v1/peers/INVALID_PEER_GROUP"
    )

    assert response.status_code == 404


def test_invalid_peer_group_error_message():

    response = client.get(
        "/api/v1/peers/INVALID_PEER_GROUP"
    )

    data = response.json()

    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_company_peer_comparison_returns_200():

    response = client.get(
        "/api/v1/companies/TCS/peers/compare"
    )

    assert response.status_code == 200


def test_company_peer_comparison_structure():

    response = client.get(
        "/api/v1/companies/TCS/peers/compare"
    )

    data = response.json()

    assert "company_id" in data
    assert "company_name" in data
    assert "peer_group" in data
    assert "year" in data
    assert "benchmark" in data
    assert "metrics" in data


def test_company_peer_comparison_has_eight_metrics():

    response = client.get(
        "/api/v1/companies/TCS/peers/compare"
    )

    data = response.json()

    assert len(data["metrics"]) == 8


def test_company_peer_comparison_metric_structure():

    response = client.get(
        "/api/v1/companies/TCS/peers/compare"
    )

    data = response.json()

    for metric in data["metrics"]:

        assert "metric" in metric
        assert "company" in metric
        assert "peer_average" in metric
        assert "benchmark" in metric


def test_invalid_company_peer_comparison_returns_404():

    response = client.get(
        "/api/v1/companies/INVALID/peers/compare"
    )

    assert response.status_code == 404