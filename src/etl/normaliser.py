import re

import pandas as pd


TICKER_MAPPING = {
    "AGTL": "ATGL"
}


def normalize_year(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    match = re.search(
        r"\b(19|20)\d{2}\b",
        value
    )

    if match:
        return int(match.group())

    return None


def normalize_period(value):
    """
    Parse a source financial period label.

    Examples:
    Mar 2024
        -> year=2024
        -> period_type=ANNUAL
        -> period_months=12

    TTM
        -> year=None
        -> period_type=TTM
        -> period_months=12

    Mar 2016 9m
        -> year=2016
        -> period_type=PARTIAL
        -> period_months=9

    Mar 2023 15
        -> year=2023
        -> period_type=PARTIAL
        -> period_months=15
    """

    if pd.isna(value):
        return {
            "year": None,
            "period_type": None,
            "period_months": None,
        }

    period_label = str(value).strip()

    if not period_label:
        return {
            "year": None,
            "period_type": None,
            "period_months": None,
        }

    upper_label = period_label.upper()

    if upper_label == "TTM":
        return {
            "year": None,
            "period_type": "TTM",
            "period_months": 12,
        }

    year = normalize_year(
        period_label
    )

    if year is None:
        return {
            "year": None,
            "period_type": None,
            "period_months": None,
        }

    partial_month_match = re.search(
        r"\b(\d{1,2})\s*[Mm]\b",
        period_label
    )

    if partial_month_match:
        return {
            "year": year,
            "period_type": "PARTIAL",
            "period_months": int(
                partial_month_match.group(1)
            ),
        }

    trailing_number_match = re.search(
        r"\b(19|20)\d{2}\s+(\d{1,2})\s*$",
        period_label
    )

    if trailing_number_match:
        return {
            "year": year,
            "period_type": "PARTIAL",
            "period_months": int(
                trailing_number_match.group(2)
            ),
        }

    return {
        "year": year,
        "period_type": "ANNUAL",
        "period_months": 12,
    }


def normalize_ticker(value):
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    value = value.replace(".NS", "")
    value = value.replace(".BO", "")
    value = value.replace(" ", "")

    value = TICKER_MAPPING.get(
        value,
        value
    )

    return value


def normalize_columns(df):
    df.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("&", "and")
        .replace("%", "pct")
        for column in df.columns
    ]

    return df