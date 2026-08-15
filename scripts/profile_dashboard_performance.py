import time
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.dashboard.utils.db import (
    get_company_info,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_valuation,
    get_company_insights,
)


TICKERS = [
    "TCS",
    "INFY",
    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
]

MAX_TIME = 3.0


def load_company_profile(company_id):
    """
    Execute the same database calls required
    by the Company Profile dashboard page.
    """

    get_company_info(company_id)
    get_ratios(company_id)
    get_pl(company_id)
    get_bs(company_id)
    get_cf(company_id)
    get_valuation(company_id)
    get_company_insights(company_id)


def main():

    print("=" * 60)
    print("N100 COMPANY PROFILE DASHBOARD PERFORMANCE TEST")
    print("=" * 60)

    results = []

    print("\nIndividual profile load times:")
    print("-" * 60)

    for ticker in TICKERS:

        start = time.perf_counter()

        try:
            load_company_profile(ticker)

            elapsed = time.perf_counter() - start

            results.append({
                "ticker": ticker,
                "time": elapsed,
                "success": True,
            })

            print(
                f"{ticker:<12} | "
                f"{elapsed:.3f} seconds | "
                f"PASS"
            )

        except Exception as error:

            elapsed = time.perf_counter() - start

            results.append({
                "ticker": ticker,
                "time": elapsed,
                "success": False,
            })

            print(
                f"{ticker:<12} | "
                f"{elapsed:.3f} seconds | "
                f"FAIL | "
                f"{error}"
            )

    successful = [
        result
        for result in results
        if result["success"]
    ]

    print("\n" + "=" * 60)

    if successful:

        average_time = sum(
            result["time"]
            for result in successful
        ) / len(successful)

        slowest_time = max(
            result["time"]
            for result in successful
        )

        print(
            f"Successful profiles : "
            f"{len(successful)}/{len(TICKERS)}"
        )

        print(
            f"Average load time   : "
            f"{average_time:.3f} seconds"
        )

        print(
            f"Slowest load time   : "
            f"{slowest_time:.3f} seconds"
        )

    print("=" * 60)

    all_under_limit = (
        len(successful) == len(TICKERS)
        and all(
            result["time"] < MAX_TIME
            for result in successful
        )
    )

    if all_under_limit:

        print(
            f"PASS: All {len(TICKERS)} company profiles "
            f"loaded within {MAX_TIME:.0f} seconds."
        )

    else:

        print(
            f"FAIL: One or more profiles "
            f"exceeded {MAX_TIME:.0f} seconds."
        )


if __name__ == "__main__":
    main()