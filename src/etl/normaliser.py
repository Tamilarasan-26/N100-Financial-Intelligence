import re
import pandas as pd


TICKER_MAPPING = {
    "AGTL": "ATGL"
}


def normalize_year(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    match = re.search(r"\b(19|20)\d{2}\b", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    value = value.replace(".NS", "")
    value = value.replace(".BO", "")
    value = value.replace(" ", "")

    value = TICKER_MAPPING.get(value, value)

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