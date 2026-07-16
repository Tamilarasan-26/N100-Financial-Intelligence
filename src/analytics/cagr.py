from dataclasses import dataclass
from typing import Optional


NORMAL = "NORMAL"
DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
TURNAROUND = "TURNAROUND"
BOTH_NEGATIVE = "BOTH_NEGATIVE"
ZERO_BASE = "ZERO_BASE"
INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class CAGRResult:
    value: Optional[float]
    flag: str


def calculate_cagr(
    start_value,
    end_value,
    years
):
    """
    Calculate Compound Annual Growth Rate.

    Formula:
        ((end / start) ** (1 / years) - 1) * 100

    CAGR value and edge-case flag are returned
    separately.
    """

    if (
        start_value is None
        or end_value is None
        or years is None
        or years <= 0
    ):
        return CAGRResult(
            value=None,
            flag=INSUFFICIENT
        )

    if start_value == 0:
        return CAGRResult(
            value=None,
            flag=ZERO_BASE
        )

    if (
        start_value > 0
        and end_value < 0
    ):
        return CAGRResult(
            value=None,
            flag=DECLINE_TO_LOSS
        )

    if (
        start_value < 0
        and end_value > 0
    ):
        return CAGRResult(
            value=None,
            flag=TURNAROUND
        )

    if (
        start_value < 0
        and end_value < 0
    ):
        return CAGRResult(
            value=None,
            flag=BOTH_NEGATIVE
        )

    if (
        start_value > 0
        and end_value >= 0
    ):
        cagr_value = (
            (
                end_value / start_value
            ) ** (1 / years)
            - 1
        ) * 100

        return CAGRResult(
            value=cagr_value,
            flag=NORMAL
        )

    return CAGRResult(
        value=None,
        flag=INSUFFICIENT
    )


def calculate_period_cagr(
    records,
    value_column,
    period_years
):
    """
    Calculate CAGR for a requested period.

    records must contain:
        year
        requested value column

    Example:
        value_column = "sales"
        period_years = 5

    The function uses the latest available year
    and the exact requested base year.
    """

    if records is None:
        return CAGRResult(
            value=None,
            flag=INSUFFICIENT
        )

    rows = list(records)

    if not rows:
        return CAGRResult(
            value=None,
            flag=INSUFFICIENT
        )

    valid_rows = []

    for row in rows:
        year = row.get("year")
        value = row.get(value_column)

        if year is None or value is None:
            continue

        valid_rows.append(
            {
                "year": int(year),
                "value": value
            }
        )

    if not valid_rows:
        return CAGRResult(
            value=None,
            flag=INSUFFICIENT
        )

    year_to_value = {
        row["year"]: row["value"]
        for row in valid_rows
    }

    latest_year = max(year_to_value)

    base_year = (
        latest_year - period_years
    )

    if (
        latest_year not in year_to_value
        or base_year not in year_to_value
    ):
        return CAGRResult(
            value=None,
            flag=INSUFFICIENT
        )

    return calculate_cagr(
        start_value=year_to_value[base_year],
        end_value=year_to_value[latest_year],
        years=period_years
    )


def calculate_growth_cagrs(records):
    """
    Calculate Revenue, PAT and EPS CAGR
    for 3Y, 5Y and 10Y periods.
    """

    metrics = {
        "revenue": "sales",
        "pat": "net_profit",
        "eps": "eps"
    }

    periods = [
        3,
        5,
        10
    ]

    results = {}

    for metric_name, column_name in metrics.items():
        for period in periods:
            result = calculate_period_cagr(
                records=records,
                value_column=column_name,
                period_years=period
            )

            key = (
                f"{metric_name}_cagr_"
                f"{period}y"
            )

            results[key] = result.value

            results[
                f"{key}_flag"
            ] = result.flag

    return results