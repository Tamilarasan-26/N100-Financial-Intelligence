import time
import requests


BASE_URL = "http://127.0.0.1:8000/api/v1"

TICKERS = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
]

MAX_TIME = 3.0


def run_company_profile_test(ticker):
    """Measure company profile API response time."""

    url = f"{BASE_URL}/companies/{ticker}"

    start = time.perf_counter()

    response = requests.get(
        url,
        timeout=10,
    )

    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


def main():

    print("=" * 60)
    print("N100 COMPANY PROFILE PERFORMANCE TEST")
    print("=" * 60)

    results = []

    print("\nIndividual request results:")
    print("-" * 60)

    for ticker in TICKERS:

        status_code, elapsed = run_company_profile_test(ticker)

        results.append(elapsed)

        print(
            f"{ticker:<12} | "
            f"HTTP {status_code} | "
            f"{elapsed:.3f} seconds"
        )

    print("\n" + "=" * 60)

    max_time = max(results)
    average_time = sum(results) / len(results)

    successful = len(results)

    print(f"Successful requests : {successful}/{len(TICKERS)}")
    print(f"Average response    : {average_time:.3f} seconds")
    print(f"Slowest response    : {max_time:.3f} seconds")

    print("=" * 60)

    if max_time < MAX_TIME:
        print(
            f"PASS: All {len(TICKERS)} company profiles "
            f"loaded within {MAX_TIME:.0f} seconds."
        )
    else:
        print(
            f"FAIL: At least one company profile "
            f"exceeded {MAX_TIME:.0f} seconds."
        )


if __name__ == "__main__":
    main()
