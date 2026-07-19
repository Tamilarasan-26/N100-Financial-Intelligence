import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"
PEER_GROUP_PATH = PROJECT_ROOT / "data" / "raw" / "peer_groups.xlsx"


def load_peer_groups():
    """
    Load peer group mapping.
    """

    return pd.read_excel(PEER_GROUP_PATH)


def load_financial_ratios():
    """
    Load financial ratios from SQLite.
    """

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        con
    )
    
    con.close()

    return df

def calculate_percentile(df, metric, ascending=True):
    """
    Calculate percentile rank within each peer group.
    """

    percentile = (
        df.groupby(["peer_group_name", "year"])[metric]
          .rank(
              pct=True,
              ascending=ascending
          )
    )

    return percentile



def create_peer_percentiles_table():

    con = sqlite3.connect(DATABASE_PATH)

    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS peer_percentiles (

        company_id TEXT,
        peer_group_name TEXT,
        metric TEXT,
        value REAL,
        percentile_rank REAL,
        year INTEGER

    )
    """)

    con.commit()
    con.close()

peer_groups = load_peer_groups()
financial_ratios = load_financial_ratios()

merged_df = pd.merge(
    financial_ratios,
    peer_groups,
    on="company_id",
    how="left"
)

# ROE
merged_df["roe_percentile"] = calculate_percentile(
    merged_df,
    "return_on_equity_pct"
)

# ROCE
merged_df["roce_percentile"] = calculate_percentile(
    merged_df,
    "return_on_capital_employed_pct"
)

# Net Profit Margin
merged_df["npm_percentile"] = calculate_percentile(
    merged_df,
    "net_profit_margin_pct"
)

# Debt to Equity (inverse)
merged_df["de_percentile"] = calculate_percentile(
    merged_df,
    "debt_to_equity",
    ascending=False
)

# Free Cash Flow
merged_df["fcf_percentile"] = calculate_percentile(
    merged_df,
    "free_cash_flow_cr"
)

# PAT CAGR
merged_df["pat_percentile"] = calculate_percentile(
    merged_df,
    "pat_cagr_5y_pct"
)

# Revenue CAGR
merged_df["revenue_percentile"] = calculate_percentile(
    merged_df,
    "revenue_cagr_5y_pct"
)

# EPS CAGR
merged_df["eps_percentile"] = calculate_percentile(
    merged_df,
    "eps_cagr_5y_pct"
)

# Interest Coverage
merged_df["interest_percentile"] = calculate_percentile(
    merged_df,
    "interest_coverage"
)

# Asset Turnover
merged_df["asset_turnover_percentile"] = calculate_percentile(
    merged_df,
    "asset_turnover"
)

metric_map = {
    "ROE": (
        "return_on_equity_pct",
        "roe_percentile"
    ),

    "ROCE": (
        "return_on_capital_employed_pct",
        "roce_percentile"
    ),

    "Net Profit Margin": (
        "net_profit_margin_pct",
        "npm_percentile"
    ),

    "Debt To Equity": (
        "debt_to_equity",
        "de_percentile"
    ),

    "Free Cash Flow": (
        "free_cash_flow_cr",
        "fcf_percentile"
    ),

    "PAT CAGR 5Y": (
        "pat_cagr_5y_pct",
        "pat_percentile"
    ),

    "Revenue CAGR 5Y": (
        "revenue_cagr_5y_pct",
        "revenue_percentile"
    ),

    "EPS CAGR 5Y": (
        "eps_cagr_5y_pct",
        "eps_percentile"
    ),

    "Interest Coverage": (
        "interest_coverage",
        "interest_percentile"
    ),

    "Asset Turnover": (
        "asset_turnover",
        "asset_turnover_percentile"
    )
}

records = []

for metric_name, (value_col, percentile_col) in metric_map.items():

    temp = merged_df[
        [
            "company_id",
            "peer_group_name",
            "year",
            value_col,
            percentile_col
        ]
    ].copy()

    temp.columns = [
        "company_id",
        "peer_group_name",
        "year",
        "value",
        "percentile_rank"
    ]

    temp["metric"] = metric_name

    records.append(temp)

peer_percentiles = pd.concat(
    records,
    ignore_index=True
)

peer_percentiles = peer_percentiles.dropna(
    subset=["peer_group_name"]
)

create_peer_percentiles_table()

con = sqlite3.connect(DATABASE_PATH)

peer_percentiles.to_sql(
    "peer_percentiles",
    con,
    if_exists="replace",
    index=False
)

con.close()

print("\nPeer Percentiles Created Successfully")
print(f"Rows inserted: {len(peer_percentiles)}")
