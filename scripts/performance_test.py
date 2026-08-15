import time
import requests
from concurrent.futures import ThreadPoolExecutor


API_URL = "http://127.0.0.1:8000/api/v1/screener"


def call_screener(request_number):
    """Send one screener request and measure its response time."""

    start_time = time.perf_counter()

    try:
        response = requests.get(
            API_URL,
            params={
                "min_roe": 15
            },
            timeout=30,
        )

        elapsed = time.perf_counter() - start_time

        return {
            "request": request_number,
            "status_code": response.status_code,
            "time": elapsed,
        }

    except Exception as error:
        elapsed = time.perf_counter() - start_time

        return {
            "request": request_number,
            "status_code": None,
            "time": elapsed,
            "error": str(error),
        }


def main():
    """Run 10 concurrent screener API requests."""

    print("=" * 60)
    print("N100 SCREENER API PERFORMANCE TEST")
    print("=" * 60)

    overall_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:

        results = list(
            executor.map(
                call_screener,
                range(1, 11)
            )
        )

    total_time = time.perf_counter() - overall_start

    print("\nIndividual request results:")
    print("-" * 60)

    for result in results:

        if result["status_code"] is not None:
            print(
                f"Request {result['request']:2d} | "
                f"HTTP {result['status_code']} | "
                f"{result['time']:.3f} seconds"
            )

        else:
            print(
                f"Request {result['request']:2d} | "
                f"FAILED | "
                f"{result['error']}"
            )

    successful = [
        result
        for result in results
        if result["status_code"] == 200
    ]

    print("\n" + "=" * 60)
    print(f"Successful requests : {len(successful)}/10")
    print(f"Total elapsed time  : {total_time:.3f} seconds")

    if successful:
        average_time = sum(
            result["time"]
            for result in successful
        ) / len(successful)

        max_time = max(
            result["time"]
            for result in successful
        )

        print(f"Average response    : {average_time:.3f} seconds")
        print(f"Slowest response    : {max_time:.3f} seconds")

    print("=" * 60)

    if len(successful) == 10 and total_time < 10:
        print(
            "PASS: 10 concurrent requests "
            "completed within 10 seconds."
        )
    else:
        print(
            "FAIL: Performance target "
            "was not achieved."
        )


if __name__ == "__main__":
    main()