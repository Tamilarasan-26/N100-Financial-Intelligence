import sqlite3
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_FOLDER = PROJECT_ROOT / "reports" / "radar_charts"

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


def load_peer_groups():

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM peer_groups",
        con
    )

    con.close()

    return df


def load_financial_ratios():

    con = sqlite3.connect(DATABASE_PATH)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        con
    )

    con.close()

    return df


def get_company_data(financial_df, company_id):

    company = financial_df[
        (financial_df["company_id"] == company_id) &
        (financial_df["period_type"] == "ANNUAL")
    ].copy()

    company = company.sort_values("year")

    return company.iloc[-1]


def get_peer_group(peer_df, company_id):

    company = peer_df[
        peer_df["company_id"] == company_id
    ]

    if company.empty:
        return None

    return company["peer_group_name"].iloc[0]


def get_peer_companies(peer_df, peer_group):

    return peer_df[
        peer_df["peer_group_name"] == peer_group
    ]

def get_peer_average(financial_df, peer_df, peer_group, year):

    peer_company_ids = peer_df[
        peer_df["peer_group_name"] == peer_group
    ]["company_id"].unique()

    peer_data = financial_df[
        (financial_df["company_id"].isin(peer_company_ids)) &
        (financial_df["period_type"] == "ANNUAL") &
        (financial_df["year"] == year)
    ]

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "cfo_quality_score",
        "pat_cagr_5y_pct",
        "revenue_cagr_5y_pct",
        "composite_quality_score"
    ]

    return peer_data[metrics].mean()

def get_nifty100_average(financial_df, year):

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "cfo_quality_score",
        "pat_cagr_5y_pct",
        "revenue_cagr_5y_pct",
        "composite_quality_score"
    ]

    nifty_data = financial_df[
        (financial_df["period_type"] == "ANNUAL") &
        (financial_df["year"] == year)
    ]

    return nifty_data[metrics].mean()

def create_radar_chart(company, peer_average, comparison_label):

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "cfo_quality_score",
        "pat_cagr_5y_pct",
        "revenue_cagr_5y_pct",
        "composite_quality_score"
    ]

    labels = [
        "ROE",
        "ROCE",
        "NPM",
        "D/E",
        "FCF Score",
        "PAT CAGR",
        "Revenue CAGR",
        "Quality Score"
    ]

    company_values = company[metrics].tolist()
    peer_values = peer_average[metrics].tolist()

    # close the polygon
    company_values += company_values[:1]
    peer_values += peer_values[:1]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    fig = plt.figure(figsize=(8, 8))

    ax = plt.subplot(111, polar=True)

    ax.plot(
        angles,
        company_values,
        linewidth=2,
        label=company["company_id"]
    )

    ax.fill(
        angles,
        company_values,
        alpha=0.25
    )

    ax.plot(
        angles,
        peer_values,
        linewidth=2,
        linestyle="--",
        label=comparison_label
    )


    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_title(
        f"{company['company_id']} vs {comparison_label} ({int(company['year'])})"
    )

    plt.legend(loc="upper right")

    output_path = OUTPUT_FOLDER / f"{company['company_id']}_radar.png"

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    return output_path

# ----------------------------
# Testing
# ----------------------------

peer_df = load_peer_groups()

financial_df = load_financial_ratios()

company_ids = financial_df["company_id"].dropna().unique()

for company_id in company_ids:

    company = get_company_data(
        financial_df,
        company_id
    )

    peer_group = get_peer_group(
    peer_df,
    company_id
    )

    if peer_group is None:
        peer_average = get_nifty100_average(
            financial_df,
            company["year"]
        )
        comparison_label = "Nifty100 Average"

    else:
        peer_average = get_peer_average(
            financial_df,
            peer_df,
            peer_group,
            company["year"]
        )
        comparison_label = "Peer Average"   

    chart_path = create_radar_chart(
        company,
        peer_average,
        comparison_label
    )

    print(f"Saved: {chart_path}")

