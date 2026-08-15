import sys
from pathlib import Path

from fastapi.testclient import TestClient


# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from src.api.main import app


client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_status_is_ok():
    response = client.get("/api/v1/health")

    data = response.json()

    assert data["status"] == "ok"


def test_health_contains_db_row_counts():
    response = client.get("/api/v1/health")

    data = response.json()

    assert "db_row_counts" in data


def test_health_contains_required_tables():
    response = client.get("/api/v1/health")

    data = response.json()

    expected_tables = {
        "companies",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "financial_ratios",
        "market_cap",
        "stock_prices",
        "peer_groups",
        "peer_percentiles",
        "documents",
    }

    assert expected_tables.issubset(
        set(data["db_row_counts"].keys())
    )


def test_health_row_counts_are_valid():
    response = client.get("/api/v1/health")

    data = response.json()

    for table, count in data["db_row_counts"].items():
        assert isinstance(count, int)
        assert count >= 0