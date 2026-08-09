from pathlib import Path
import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports"
CHART_DIR = PROJECT_ROOT / "reports" / "charts"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

risk_df = pd.read_excel(
    PROJECT_ROOT / "output" / "risk_scores.xlsx"
)

sector_df = pd.read_excel(
    PROJECT_ROOT / "data" / "raw" / "sectors.xlsx"
)

df = risk_df.merge(
    sector_df,
    on="company_id",
    how="left"
)

styles = getSampleStyleSheet()

pdf = SimpleDocTemplate(
    str(REPORT_DIR / "Portfolio_Summary.pdf")
)

elements = []

# -----------------------------
# Portfolio Statistics
# -----------------------------

total_companies = len(df)

avg_risk_score = df["risk_score"].mean()

avg_cfo_score = df["cfo_quality_score"].mean()

avg_fcf_conversion = df["fcf_conversion_pct"].mean()

low_risk = len(df[df["risk_category"] == "LOW"])

medium_risk = len(df[df["risk_category"] == "MEDIUM"])

high_risk = len(df[df["risk_category"] == "HIGH"])

# -----------------------------
# PAGE 1
# -----------------------------

elements.append(
    Paragraph(
        "<b>Nifty 100 Financial Intelligence Portfolio Report</b>",
        styles["Title"]
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        "Executive Summary",
        styles["Heading1"]
    )
)

elements.append(
    Paragraph(
        "This report summarizes the financial health and risk analysis "
        "of the Nifty 100 companies using financial ratios, cash flow "
        "analysis, capital allocation, and rule-based risk scoring.",
        styles["Normal"]
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        "<b>Portfolio Statistics</b>",
        styles["Heading2"]
    )
)

elements.append(
    Paragraph(
        f"Total Companies : {total_companies}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Average Risk Score : {avg_risk_score:.2f}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Average CFO Quality Score : {avg_cfo_score:.2f}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Average FCF Conversion : {avg_fcf_conversion:.2f}%",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Low Risk Companies : {low_risk}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"Medium Risk Companies : {medium_risk}",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        f"High Risk Companies : {high_risk}",
        styles["Normal"]
    )
)

elements.append(PageBreak())

# -----------------------------
# PAGE 2
# -----------------------------

elements.append(
    Paragraph(
        "<b>Risk Distribution</b>",
        styles["Heading2"]
    )
)

elements.append(
    Image(
        str(CHART_DIR / "portfolio_risk_distribution.png"),
        width=420,
        height=250
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        "<b>Capital Allocation Distribution</b>",
        styles["Heading2"]
    )
)

elements.append(
    Image(
        str(CHART_DIR / "portfolio_capital_allocation.png"),
        width=420,
        height=250
    )
)

elements.append(PageBreak())

# -----------------------------
# PAGE 3
# -----------------------------

elements.append(
    Paragraph(
        "<b>Sector Distribution</b>",
        styles["Heading2"]
    )
)

elements.append(
    Image(
        str(CHART_DIR / "portfolio_sector_distribution.png"),
        width=420,
        height=250
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        "<b>Top 10 Highest Risk Companies</b>",
        styles["Heading2"]
    )
)

elements.append(
    Image(
        str(CHART_DIR / "portfolio_top10_risk.png"),
        width=420,
        height=250
    )
)

elements.append(PageBreak())

# -----------------------------
# PAGE 4
# -----------------------------

elements.append(
    Paragraph(
        "<b>Top 10 Lowest Risk Companies</b>",
        styles["Heading2"]
    )
)

elements.append(
    Image(
        str(CHART_DIR / "portfolio_top10_low_risk.png"),
        width=420,
        height=250
    )
)

elements.append(Spacer(1, 20))

elements.append(
    Paragraph(
        "<b>Portfolio Insights</b>",
        styles["Heading2"]
    )
)

elements.append(
    Paragraph(
        "• Majority of companies fall into the LOW and MEDIUM risk categories.",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        "• Companies with strong CFO quality generally have lower financial risk.",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        "• Capital allocation patterns indicate a mix of self-funded growth and externally funded expansion.",
        styles["Normal"]
    )
)

elements.append(
    Paragraph(
        "<b>Recommendations</b>",
        styles["Heading2"]
    )
)

elements.append(
    Paragraph(
        "Use this portfolio report as a high-level screening tool before conducting detailed company-level analysis.",
        styles["Normal"]
    )
)

pdf.build(elements)

print("Portfolio Summary PDF Generated Successfully!")