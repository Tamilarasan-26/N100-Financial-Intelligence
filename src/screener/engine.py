import sqlite3
from pathlib import Path

import pandas as pd
import yaml


# ==========================
# Project Paths
# ==========================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"


# ==========================
# Load Financial Ratios
# ==========================

def load_financial_ratios():
    """
    Load financial_ratios table from SQLite.
    """

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        con
    )

    con.close()

    return df


# ==========================
# Load Market Cap
# ==========================

def load_market_cap():
    """
    Load market_cap table from SQLite.
    """

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM market_cap",
        con
    )

    con.close()

    return df


# ==========================
# Load Profit & Loss
# ==========================

def load_profit_and_loss():
    """
    Load profitandloss table from SQLite.
    """

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM profitandloss",
        con
    )

    con.close()

    # Remove duplicate rows based on the merge keys
    df = df.drop_duplicates(
        subset=["company_id", "year", "period_type"],
        keep="first"
    )

    return df
# ==========================
# Load Companies
# ==========================

def load_companies():
    """
    Load companies table from SQLite.
    """

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name,
            broad_sector,
            sub_sector,
            market_cap_category
        FROM companies
        """,
        con
    )

    con.close()

    return df

# ==========================
# Merge Financial Data
# ==========================

def merge_data(financial_ratios, market_cap, profit_loss, companies):
    """
    Merge financial ratios, market cap and profit & loss.
    """

    merged_df = pd.merge(
        financial_ratios,
        market_cap,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_market")
    )

    merged_df = pd.merge(
    merged_df,
    profit_loss,
    on=["company_id", "year", "period_type"],
    how="left",
    suffixes=("", "_pl")
    )
    
    merged_df = pd.merge(
    merged_df,
    companies,
    on="company_id",
    how="left"
    )

    return merged_df


# ==========================
# Load YAML Config
# ==========================

def load_config():
    """
    Load screener configuration.
    """

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config

# ==========================
# Preset Screeners
# ==========================

def apply_preset(df, preset):
    """
    Apply predefined screening presets.
    """

    preset_df = df.copy()

    if preset == "quality_compounder":

        preset_df = preset_df[
            (preset_df["return_on_equity_pct"] > 15) &
            (
                (preset_df["broad_sector"] == "Financials") |
                (preset_df["debt_to_equity"] < 1.0)
            ) &
            (preset_df["free_cash_flow_cr"] > 0) &
            (preset_df["revenue_cagr_5y_pct"] > 10)
        ]
    elif preset == "value_pick":

        preset_df = preset_df[
            (preset_df["pe_ratio"] < 20) &
            (preset_df["pb_ratio"] < 3.0) &
            (
                (preset_df["broad_sector"] == "Financials") |
                (preset_df["debt_to_equity"] < 2.0)
            ) &
            (preset_df["dividend_yield_pct"] > 1)
        ]
    elif preset == "growth_accelerator":

        preset_df = preset_df[
            (preset_df["pat_cagr_5y_pct"] > 20) &
            (preset_df["revenue_cagr_5y_pct"] > 15) &
            (
                (preset_df["broad_sector"] == "Financials") |
                (preset_df["debt_to_equity"] < 2.0)
            )
        ]
    elif preset == "dividend_champion":

        preset_df = preset_df[
            (preset_df["dividend_yield_pct"] > 4) &
            (preset_df["dividend_payout_ratio_pct"] < 70) &
            (preset_df["free_cash_flow_cr"] > 0)
        ]
    elif preset == "debt_free_bluechip":

        preset_df = preset_df[
            (preset_df["debt_to_equity"] == 0) &
            (preset_df["return_on_equity_pct"] > 12) &
            (preset_df["sales"] > 5000)
        ]
    elif preset == "turnaround_watch":

    # Sort by company and year
        preset_df = preset_df.sort_values(
            by=["company_id", "year"]
        )

    # Previous year's Debt-to-Equity
        preset_df["previous_debt_to_equity"] = (
            preset_df.groupby("company_id")["debt_to_equity"]
            .shift(1)
        )

        preset_df = preset_df[
            (preset_df["revenue_cagr_3y_pct"] > 15) &
            (preset_df["free_cash_flow_cr"] > 0) &
            (
                (preset_df["interest_coverage"] > 2) |
                (preset_df["icr_label"] == "Debt Free")
            ) &
            (preset_df["return_on_equity_pct"] > 10) &
            (
                preset_df["debt_to_equity"] <
                preset_df["previous_debt_to_equity"]
            )
        ]

    return preset_df


# ==========================
# Apply Filters
# ==========================

def apply_filters(df, config):
    """
    Apply all screening filters.
    """

    filters = config["filters"]

    filtered_df = df.copy()

    required_columns = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5y_pct",
    "pat_cagr_5y_pct",
    "operating_profit_margin_pct",
    "interest_coverage",
    "free_cash_flow_cr",
    "asset_turnover",
    "pe_ratio",
    "pb_ratio",
    "market_cap_crore",
    "dividend_yield_pct",
    "sales",
    "net_profit",
    "eps_cagr_5y_pct"
    ]

    filtered_df = filtered_df.dropna(subset=required_columns)

    # ROE
    filtered_df = filtered_df[
        filtered_df["return_on_equity_pct"] >= filters["min_roe"]
    ]

    # Debt to Equity
    filtered_df = filtered_df[
        (
            filtered_df["broad_sector"] == "Financials"
        ) |
        (
            filtered_df["debt_to_equity"] <= filters["max_debt_to_equity"]
        )
    ]

    # Revenue CAGR (5Y)
    filtered_df = filtered_df[
        filtered_df["revenue_cagr_5y_pct"] >= filters["min_revenue_cagr_5y"]
    ]

    # PAT CAGR (5Y)
    filtered_df = filtered_df[
        filtered_df["pat_cagr_5y_pct"] >= filters["min_pat_cagr_5y"]
    ]

    # Operating Profit Margin
    filtered_df = filtered_df[
        filtered_df["operating_profit_margin_pct"] >= filters["min_opm"]
    ]

    # Interest Coverage
    filtered_df = filtered_df[
        (filtered_df["interest_coverage"] >= filters["min_interest_coverage"]) |
        (filtered_df["icr_label"] == "Debt Free")
    ]

    # Free Cash Flow
    filtered_df = filtered_df[
        filtered_df["free_cash_flow_cr"] >= filters["min_fcf"]
    ]

    # Asset Turnover
    filtered_df = filtered_df[
        filtered_df["asset_turnover"] >= filters["min_asset_turnover"]
    ]
    
    # PE Ratio
    filtered_df = filtered_df[
        filtered_df["pe_ratio"] <= filters["max_pe"]
    ]

    # PB Ratio
    filtered_df = filtered_df[
        filtered_df["pb_ratio"] <= filters["max_pb"]
    ]

    # Market Capitalization
    filtered_df = filtered_df[
        filtered_df["market_cap_crore"] >= filters["min_market_cap"]
    ]

    # Dividend Yield
    filtered_df = filtered_df[
        filtered_df["dividend_yield_pct"] >= filters["min_dividend_yield"]
    ]

    # Sales
    filtered_df = filtered_df[
        filtered_df["sales"] >= filters["min_sales"]
    ]

    # Net Profit
    filtered_df = filtered_df[
        filtered_df["net_profit"] >= filters["min_net_profit"]
    ]

    # EPS CAGR (5Y)
    filtered_df = filtered_df[
        filtered_df["eps_cagr_5y_pct"] >= filters["min_eps_cagr_5y"]
    ]

    return filtered_df

# ==========================
# Winsorization Helper
# ==========================

def winsorize_series(series):
    """
    Clip values to the 10th and 90th percentiles.
    """

    lower = series.quantile(0.10)
    upper = series.quantile(0.90)

    return series.clip(lower=lower, upper=upper)

# ==========================
# Sector Normalization Helper
# ==========================

def normalize_by_sector(df, score_column):
    """
    Normalize a score within each broad sector using Min-Max scaling.
    """

    normalized = (
        df.groupby("broad_sector")[score_column]
          .transform(
              lambda x: (
                  (x - x.min()) / (x.max() - x.min())
                  if x.max() != x.min()
                  else 0.5
              )
          )
    )

    return normalized

# ==========================
# Composite Quality Score
# ==========================

def add_composite_score(df):
    """
    Calculate Composite Quality Score (Day 17).
    """

    scored_df = df.copy()
    
    # Fill missing values for scoring metrics

    score_columns = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "free_cash_flow_cr",
        "cfo_quality_score",
        "revenue_cagr_5y_pct",
        "pat_cagr_5y_pct",
        "debt_to_equity",
        "interest_coverage"
    ]

    scored_df = scored_df.dropna(subset=score_columns)

    # -----------------------------
    # Winsorize Metrics
    # -----------------------------

    # Profitability
    scored_df["roe_score"] = winsorize_series(
        scored_df["return_on_equity_pct"]
    )

    scored_df["roce_score"] = winsorize_series(
        scored_df["return_on_capital_employed_pct"]
    )

    scored_df["npm_score"] = winsorize_series(
        scored_df["net_profit_margin_pct"]
    )

    # Cash Quality
    scored_df["fcf_score"] = winsorize_series(
        scored_df["free_cash_flow_cr"]
    )

    scored_df["cfo_pat_score"] = winsorize_series(
        scored_df["cfo_quality_score"]
    )

    # Growth
    scored_df["revenue_growth_score"] = winsorize_series(
        scored_df["revenue_cagr_5y_pct"]
    )

    scored_df["pat_growth_score"] = winsorize_series(
        scored_df["pat_cagr_5y_pct"]
    )

    # Leverage
    scored_df["de_score"] = winsorize_series(
        -scored_df["debt_to_equity"]
    )

    scored_df["icr_score"] = winsorize_series(
        scored_df["interest_coverage"]
    )
    
    # -----------------------------
    # Sector Normalization
    # -----------------------------

    scored_df["roe_score"] = normalize_by_sector(
        scored_df,
        "roe_score"
    )

    scored_df["roce_score"] = normalize_by_sector(
        scored_df,
        "roce_score"
    )

    scored_df["npm_score"] = normalize_by_sector(
        scored_df,
        "npm_score"
    )

    scored_df["fcf_score"] = normalize_by_sector(
        scored_df,
        "fcf_score"
    )

    scored_df["cfo_pat_score"] = normalize_by_sector(
        scored_df,
        "cfo_pat_score"
    )

    scored_df["revenue_growth_score"] = normalize_by_sector(
        scored_df,
        "revenue_growth_score"
    )

    scored_df["pat_growth_score"] = normalize_by_sector(
        scored_df,
        "pat_growth_score"
    )

    scored_df["de_score"] = normalize_by_sector(
        scored_df,
        "de_score"
    )

    scored_df["icr_score"] = normalize_by_sector(
        scored_df,
        "icr_score"
    )


    # -----------------------------
    # Weighted Composite Score
    # -----------------------------

    scored_df["composite_quality_score"] = (

        # Profitability (35%)
        scored_df["roe_score"] * 0.15 +
        scored_df["roce_score"] * 0.10 +
        scored_df["npm_score"] * 0.10 +

        # Cash Quality (30%)
        scored_df["fcf_score"] * 0.15 +
        scored_df["cfo_pat_score"] * 0.10 +
        (scored_df["free_cash_flow_cr"] > 0).astype(int) * 0.05 +

        # Growth (20%)
        scored_df["revenue_growth_score"] * 0.10 +
        scored_df["pat_growth_score"] * 0.10 +

        # Leverage (15%)
        scored_df["de_score"] * 0.10 +
        scored_df["icr_score"] * 0.05

    ) * 100
    
    scored_df = scored_df.sort_values(
    by="composite_quality_score",
    ascending=False
    )

    return scored_df

# ==========================
# Keep Latest Year
# ==========================

def keep_latest_year(df):
    """
    Keep only the latest financial year for each company.
    """

    latest_df = (
        df.sort_values("year", ascending=False)
          .drop_duplicates(subset="company_id", keep="first")
    )

    return latest_df

# ==========================
# Main
# ==========================

def main():

    ratios = load_financial_ratios()
    market_cap = load_market_cap()
    profit_loss = load_profit_and_loss()
    companies = load_companies()
   

    config = load_config()
    
    SCREEN_MODE = "preset"
    # SCREEN_MODE = "custom"

    print("=" * 60)
    print("Financial Ratios Loaded")
    print("=" * 60)

    
    print("\nFinancial Ratios Rows :", len(ratios))
    print("Market Cap Rows       :", len(market_cap))
    print("Profit & Loss Rows    :", len(profit_loss))

    print("\nConfiguration")
    print(config)

    merged_df = merge_data(
    ratios,
    market_cap,
    profit_loss,
    companies
    )
    print("\nMerged Rows :", len(merged_df))

    print("\nMerged Columns :")
    print(merged_df.columns.tolist())

    if SCREEN_MODE == "custom":

        filtered = apply_filters(
            merged_df,
            config
        )

    elif SCREEN_MODE == "preset":

       filtered = apply_preset(
        merged_df,
        "turnaround_watch"
    )

    filtered = add_composite_score(filtered)
    filtered = keep_latest_year(filtered)
    
    
    print("Unique Companies:", filtered["company_id"].nunique())
    print("Latest Years:", sorted(filtered["year"].unique(), reverse=True))
    
    print("\n" + "=" * 60)
    print("FILTER RESULTS")
    print("=" * 60)

    print("Filtered Rows :", len(filtered))

    print("\nFirst 10 Matching Companies:\n")

    print(
        filtered[
            [
                "company_id",
                "year",
                "composite_quality_score",
                "return_on_equity_pct",
                "debt_to_equity",
                "revenue_cagr_5y_pct",
                "pat_cagr_5y_pct",
                "operating_profit_margin_pct",
                "interest_coverage",
                "free_cash_flow_cr",
                "asset_turnover"
            ]
        ].head(10)
    )


if __name__ == "__main__":
    main()
    