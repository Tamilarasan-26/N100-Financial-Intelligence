from pathlib import Path
import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports" / "sector"
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

for sector in sorted(df["broad_sector"].dropna().unique()):

    sector_data = df[df["broad_sector"] == sector]

    pdf = SimpleDocTemplate(
        str(REPORT_DIR / f"{sector}_report.pdf")
    )

    elements = []

    elements.append(
        Paragraph(
            f"<b>{sector} Sector Report</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Number of Companies: {len(sector_data)}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    median_risk = sector_data["risk_score"].median()
    avg_cfo = sector_data["cfo_quality_score"].mean()

    elements.append(
        Paragraph(
            f"Median Risk Score: {median_risk:.2f}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Average CFO Quality Score: {avg_cfo:.2f}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    table_data = [
        ["Company", "Risk", "Category", "Capital Allocation"]
    ]

    for _, row in sector_data.iterrows():
        table_data.append([
            row["company_id"],
            str(row["risk_score"]),
            row["risk_category"],
            row["capital_allocation"]
        ])

    table = Table(table_data, colWidths=[90, 70, 90, 180])

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,1), (-1,-1), colors.beige),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ])
    )

    elements.append(table)

    pdf.build(elements)

    print(f"{sector} Report Generated")