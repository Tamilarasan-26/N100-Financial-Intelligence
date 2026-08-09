from pathlib import Path
import pandas as pd

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Image
)

from reportlab.lib import colors

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports" / "tearsheets"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR = PROJECT_ROOT / "reports" / "charts"

INPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "risk_scores.xlsx"
)

df = pd.read_excel(INPUT_FILE)

PROS_CONS_FILE = (
    PROJECT_ROOT
    / "output"
    / "pros_cons_generated.csv"
)

pros_cons = pd.read_csv(PROS_CONS_FILE)

styles = getSampleStyleSheet()

skipped_companies = []
generated_reports = 0
failed_reports = 0

for _, company in df.iterrows():

    company_id = company["company_id"]
    

    company_charts = pros_cons[
        pros_cons["company_id"] == company_id
    ]

    if len(company_charts) < 3:

        skipped_companies.append({
            "company_id": company_id,
            "reason": "Insufficient data"
        })

        print(f"Skipping {company_id} - insufficient data")
        continue

    print(f"Generating PDF for {company_id}...")

    pros = pros_cons[
        (pros_cons["company_id"] == company_id) &
        (pros_cons["type"] == "Pro")
    ]

    cons = pros_cons[
        (pros_cons["company_id"] == company_id) &
        (pros_cons["type"] == "Con")
    ]

    pdf = SimpleDocTemplate(
        str(REPORT_DIR / f"{company_id}_tearsheet.pdf")
    )

    elements = []

    # -------------------------
    # PAGE 1
    # -------------------------

    elements.append(
        Paragraph(
            f"<b>{company['company_id']} Company Tearsheet</b>",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Ticker : {company['company_id']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Sector : {company['sector']}",
            styles["Normal"]
        )
    )
    elements.append(
        Paragraph(
            f"Risk Category : {company['risk_category']}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Capital Allocation : {company['capital_allocation']}",
            styles["Normal"]
        )
    )

    kpi_data = [
        ["KPI", "Value"],
        ["Risk Category", company["risk_category"]],
        ["Risk Score", str(company["risk_score"])],
        ["CFO Quality", company["cfo_quality_label"]],
        ["Capital Allocation", company["capital_allocation"]],
        ["CapEx Intensity", f"{company['capex_intensity_pct']:.2f}%"],
        ["FCF Conversion", f"{company['fcf_conversion_pct']:.2f}%"]
    ]

    table = Table(
        kpi_data,
        colWidths=[220, 180]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("GRID", (0,0), (-1,-1), 1, colors.black),

            ("BACKGROUND", (0,1), (-1,-1), colors.beige),

            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0,0), (-1,0), 10),

            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("<b>ROE Trend</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_roe.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))


    elements.append(
        Paragraph("<b>Free Cash Flow Trend</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_fcf.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))



    elements.append(
        Paragraph("<b>Debt-to-Equity Trend</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_debt_equity.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))

    # -------------------------
    # PAGE 2
    # -------------------------

    elements.append(PageBreak())

    elements.append(
        Paragraph("<b>Interest Coverage Trend</b>", styles["Heading2"])
    )
    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_interest_coverage.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("<b>Balance Sheet Trend</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_balance_sheet.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("<b>Cash Flow Components</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_cashflow.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))


    elements.append(
        Paragraph("<b>Earnings Per Share Trend</b>", styles["Heading2"])
    )

    elements.append(
        Image(
            str(CHART_DIR / f"{company_id}_eps.png"),
            width=420,
            height=220
        )
    )

    elements.append(Spacer(1, 20))


    elements.append(
        Paragraph("<b>Pros</b>", styles["Heading2"])
    )

    for _, row in pros.iterrows():
        elements.append(
            Paragraph(f"• {row['text']}", styles["Normal"])
        )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("<b>Cons</b>", styles["Heading2"])
    )

    if cons.empty:
        elements.append(
            Paragraph(
                "• No major financial concerns identified based on current rule set.",
                styles["Normal"]
            )
        )
    else:
        for _, row in cons.iterrows():
            elements.append(
                Paragraph(f"• {row['text']}", styles["Normal"])
            )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Capital Allocation Badge:</b> {company['capital_allocation']}",
            styles["Heading2"]
        )
    )
    pdf.build(elements)
    
    generated_reports += 1

    print(f"{company_id} Tearsheet Generated")
    
skipped_df = pd.DataFrame(
    skipped_companies,
    columns=["company_id", "reason"]
)

skipped_df.to_csv(
    PROJECT_ROOT / "output" / "skipped_tearsheets.csv",
    index=False
)

print(f"Skipped Companies: {len(skipped_df)}")

print("\n========== Batch Summary ==========")
print(f"Total Companies   : {len(df)}")
print(f"Generated Reports : {generated_reports}")
print(f"Skipped Reports   : {len(skipped_df)}")
print(f"Failed Reports    : {failed_reports}")
print("===================================")

