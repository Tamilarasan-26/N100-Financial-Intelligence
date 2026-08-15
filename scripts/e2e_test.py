import requests
import sys


FASTAPI_URL = "http://127.0.0.1:8000"
STREAMLIT_URL = "http://localhost:8501"


def check_service(name, url):
    """Check whether a service is responding successfully."""

    try:
        response = requests.get(url, timeout=10)

        print(
            f"{name:<12} | "
            f"HTTP {response.status_code} | "
            f"{url}"
        )

        return response.status_code == 200

    except requests.RequestException as error:

        print(
            f"{name:<12} | FAIL | {error}"
        )

        return False


def main():

    print("=" * 60)
    print("N100 END-TO-END INTEGRATION TEST")
    print("=" * 60)

    print("\nService checks:")
    print("-" * 60)

    fastapi_ok = check_service(
        "FastAPI",
        f"{FASTAPI_URL}/api/v1/health"
    )

    streamlit_ok = check_service(
        "Streamlit",
        STREAMLIT_URL
    )

    print("\nAPI data check:")
    print("-" * 60)

    api_data_ok = False

    try:

        response = requests.get(
            f"{FASTAPI_URL}/api/v1/health",
            timeout=10
        )

        data = response.json()

        required_keys = [
            "status",
            "db_row_counts",
            "uptime_seconds",
            "version",
        ]

        api_data_ok = all(
            key in data
            for key in required_keys
        )

        print(
            "Health response structure | "
            f"{'PASS' if api_data_ok else 'FAIL'}"
        )

        if api_data_ok:

            print(
                f"API status              : "
                f"{data['status']}"
            )

            print(
                f"Companies               : "
                f"{data['db_row_counts']['companies']}"
            )

            print(
                f"Financial ratios        : "
                f"{data['db_row_counts']['financial_ratios']}"
            )

    except Exception as error:

        print(
            f"API data check | FAIL | {error}"
        )

    print("\n" + "=" * 60)

    if fastapi_ok and streamlit_ok and api_data_ok:

        print(
            "PASS: FastAPI and Streamlit are running "
            "simultaneously and API data is available."
        )

    else:

        print(
            "FAIL: End-to-end integration test failed."
        )

    print("=" * 60)


if __name__ == "__main__":
    main()