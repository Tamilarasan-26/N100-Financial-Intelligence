from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
)


OUTPUT = Path("docs/analyst_guide.pdf")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)


styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "GuideTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=24,
    leading=30,
    spaceAfter=20,
)

subtitle_style = ParagraphStyle(
    "GuideSubtitle",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=12,
    leading=18,
)

h1 = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=18,
    leading=22,
    spaceBefore=8,
    spaceAfter=12,
)

h2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=13,
    leading=17,
    spaceBefore=8,
    spaceAfter=8,
)

body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=9.5,
    leading=14,
    spaceAfter=7,
)

bullet = ParagraphStyle(
    "Bullet",
    parent=body,
    leftIndent=15,
    firstLineIndent=-8,
    spaceAfter=5,
)

small = ParagraphStyle(
    "Small",
    parent=body,
    fontSize=8,
    leading=11,
)


def P(text, style=body):
    return Paragraph(text, style)


def B(text):
    return Paragraph("• " + text, bullet)


def footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        0.65 * inch,
        0.4 * inch,
        "N100 Financial Intelligence Platform"
    )

    canvas.drawRightString(
        7.8 * inch,
        0.4 * inch,
        f"Page {doc.page}"
    )

    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45,
)

story = []


# ============================================================
# PAGE 1 — COVER
# ============================================================

story.append(Spacer(1, 1.3 * inch))

story.append(
    P(
        "N100 Financial Intelligence Platform",
        title_style,
    )
)

story.append(
    P(
        "Analyst User Guide",
        ParagraphStyle(
            "CoverSub",
            parent=title_style,
            fontSize=18,
        ),
    )
)

story.append(Spacer(1, 0.3 * inch))

story.append(
    P(
        "Financial analytics, valuation, risk intelligence, "
        "cash-flow analysis, stock screening, peer comparison, "
        "sector analysis and automated reporting.",
        subtitle_style,
    )
)

story.append(Spacer(1, 0.7 * inch))

story.append(
    P(
        "<b>Platform Coverage</b>",
        h2,
    )
)

coverage = [
    ["Companies", "92"],
    ["Sectors", "10"],
    ["Company Tearsheet Reports", "92"],
    ["Sector Reports", "10"],
    ["Portfolio Summary", "1"],
    ["Financial Pros & Cons", "856"],
    ["Distress Alerts", "13"],
]

table = Table(coverage, colWidths=[3.8 * inch, 1.5 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]
    )
)

story.append(table)
story.append(Spacer(1, 0.5 * inch))

story.append(P("<b>Author:</b> Tamilarasan M", subtitle_style))
story.append(P("Data Analyst | Data Science Enthusiast", subtitle_style))

story.append(PageBreak())


# ============================================================
# PAGE 2 — OVERVIEW
# ============================================================

story.append(P("1. Platform Overview", h1))

story.append(
    P(
        "The N100 Financial Intelligence Platform is a financial "
        "analytics platform designed to analyze a large-cap company "
        "universe using financial statements, ratios, valuation, "
        "risk indicators, cash-flow metrics, peer comparison, "
        "sector analysis and automated reporting."
    )
)

story.append(P("Core capabilities", h2))

for item in [
    "Financial ratio analysis",
    "Company financial profile analysis",
    "Stock screening",
    "Peer comparison",
    "Sector analysis",
    "Trend analysis",
    "Risk scoring",
    "Cash-flow intelligence",
    "Capital allocation analysis",
    "Valuation analysis",
    "Automated company tearsheets",
    "Automated sector reports",
    "Portfolio intelligence",
]:
    story.append(B(item))

story.append(P("Platform architecture", h2))

story.append(
    P(
        "The platform uses a Streamlit dashboard as the interactive "
        "analyst interface. Streamlit communicates with a FastAPI "
        "backend through HTTP requests. The backend accesses the "
        "SQLite database and returns financial intelligence data."
    )
)

story.append(
    P(
        "<b>Architecture:</b> Streamlit Dashboard → FastAPI Backend "
        "→ SQLite Database"
    )
)

story.append(P("Technology stack", h2))

for item in [
    "Python",
    "Pandas and NumPy",
    "Streamlit",
    "FastAPI and Uvicorn",
    "Plotly and Matplotlib",
    "Scikit-learn",
    "SQLite",
    "OpenPyXL",
    "ReportLab",
    "Pytest",
    "Requests",
]:
    story.append(B(item))

story.append(PageBreak())


# ============================================================
# PAGE 3 — INSTALLATION / STARTUP
# ============================================================

story.append(P("2. Installation and Application Startup", h1))

story.append(P("Create virtual environment", h2))

story.append(
    P(
        "<font name='Courier'>python -m venv .venv</font>"
    )
)

story.append(P("Activate on Windows PowerShell", h2))

story.append(
    P(
        "<font name='Courier'>.venv\\Scripts\\Activate.ps1</font>"
    )
)

story.append(P("Install dependencies", h2))

story.append(
    P(
        "<font name='Courier'>pip install -r requirements.txt</font>"
    )
)

story.append(P("Start FastAPI backend", h2))

for item in [
    "Open Terminal 1.",
    "Activate the virtual environment.",
    "Run: uvicorn src.api.main:app --reload",
    "Backend URL: http://127.0.0.1:8000",
    "API base: http://127.0.0.1:8000/api/v1",
]:
    story.append(B(item))

story.append(P("Start Streamlit dashboard", h2))

for item in [
    "Open Terminal 2.",
    "Activate the virtual environment.",
    "Run: streamlit run src/dashboard/app.py",
    "Dashboard URL: http://localhost:8501",
]:
    story.append(B(item))

story.append(P("Important", h2))

story.append(
    P(
        "Both FastAPI and Streamlit should be running simultaneously "
        "for the complete dashboard workflow."
    )
)

story.append(PageBreak())


# ============================================================
# PAGE 4 — HOME + PROFILE
# ============================================================

story.append(P("3. Home Dashboard and Company Profile", h1))

story.append(P("Home Dashboard", h2))

story.append(
    P(
        "The Home Dashboard provides a high-level overview of the "
        "company universe and key financial indicators."
    )
)

for item in [
    "Total Companies",
    "Average ROE",
    "Average P/E",
    "Average D/E",
    "Revenue CAGR",
    "Debt-Free Companies",
    "Sector Distribution",
]:
    story.append(B(item))

story.append(P("Company Profile", h2))

story.append(
    P(
        "The Company Profile page is used for detailed company-level "
        "financial analysis."
    )
)

for item in [
    "Company information",
    "Financial ratios",
    "Profit & Loss",
    "Balance Sheet",
    "Cash Flow",
    "Revenue trends",
    "ROE versus ROCE trends",
    "Generated Pros & Cons",
]:
    story.append(B(item))

story.append(P("Suggested analyst workflow", h2))

for item in [
    "Select a company.",
    "Review the company information.",
    "Check profitability ratios.",
    "Review leverage and debt indicators.",
    "Review cash-flow trends.",
    "Review historical growth.",
    "Read the generated Pros & Cons.",
]:
    story.append(B(item))

story.append(PageBreak())


# ============================================================
# PAGE 5 — SCREENER
# ============================================================

story.append(P("4. Stock Screener", h1))

story.append(
    P(
        "The Stock Screener allows analysts to filter companies using "
        "financial metrics and predefined screening conditions."
    )
)

story.append(P("Screener features", h2))

for item in [
    "Custom metric filters",
    "Preset filters",
    "Financial screening",
    "Live results",
    "CSV download",
]:
    story.append(B(item))

story.append(P("Typical screening workflow", h2))

steps = [
    "Open the Stock Screener page.",
    "Select the required financial metrics.",
    "Enter or select the desired filter conditions.",
    "Apply the filters.",
    "Review the resulting companies.",
    "Download the results when required.",
]

for i, item in enumerate(steps, 1):
    story.append(P(f"<b>{i}.</b> {item}"))

story.append(P("Analyst use cases", h2))

for item in [
    "Finding companies with stronger profitability",
    "Filtering companies by leverage",
    "Identifying companies using multiple financial conditions",
    "Creating a shortlist for deeper company analysis",
]:
    story.append(B(item))

story.append(PageBreak())


# ============================================================
# PAGE 6 — PEERS / TRENDS
# ============================================================

story.append(P("5. Peer Comparison and Trend Analysis", h1))

story.append(P("Peer Comparison", h2))

story.append(
    P(
        "The Peer Comparison page allows analysts to compare company "
        "KPIs with sector-level information."
    )
)

for item in [
    "KPI comparison",
    "Sector average",
    "Company metrics",
]:
    story.append(B(item))

story.append(P("Recommended peer-analysis workflow", h2))

for item in [
    "Select the target company.",
    "Review its key KPIs.",
    "Compare the company metrics with the sector average.",
    "Identify relative strengths and weaknesses.",
    "Use the result as supporting evidence for further analysis.",
]:
    story.append(B(item))

story.append(P("Trend Analysis", h2))

for item in [
    "Multi-metric trend charts",
    "Growth percentage labels",
    "Historical financial trends",
]:
    story.append(B(item))

story.append(
    P(
        "Trend analysis should be used to understand whether a company's "
        "financial performance is improving, stable or deteriorating over "
        "time rather than relying only on a single-year value."
    )
)

story.append(PageBreak())


# ============================================================
# PAGE 7 — SECTOR / CAPITAL
# ============================================================

story.append(P("6. Sector Analysis and Capital Allocation", h1))

story.append(P("Sector Analysis", h2))

for item in [
    "Sector bubble chart",
    "Sector KPI analysis",
    "Sector comparison",
]:
    story.append(B(item))

story.append(P("Available sectors", h2))

sectors = [
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Healthcare",
    "Industrials",
    "Information Technology",
    "Materials",
    "Real Estate",
]

for sector in sectors:
    story.append(B(sector))

story.append(P("Capital Allocation Map", h2))

for item in [
    "Capital Allocation Treemap",
    "Company distribution by allocation pattern",
]:
    story.append(B(item))

story.append(
    P(
        "The Capital Allocation page helps analysts understand how "
        "companies are distributed across capital allocation patterns."
    )
)

story.append(PageBreak())


# ============================================================
# PAGE 8 — REPORTS
# ============================================================

story.append(P("7. Automated Financial Reporting", h1))

story.append(P("Company Tearsheets", h2))

story.append(
    P(
        "The platform automatically generates a financial PDF tearsheet "
        "for each analyzed company."
    )
)

report_table = [
    ["Metric", "Result"],
    ["Total Companies", "92"],
    ["Generated Reports", "92"],
    ["Skipped Reports", "0"],
    ["Failed Reports", "0"],
]

table = Table(report_table, colWidths=[3.2 * inch, 2 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(table)

story.append(Spacer(1, 10))

story.append(
    P(
        "Company reports are stored under "
        "<font name='Courier'>reports/tearsheets/</font>."
    )
)

story.append(P("Sector Reports", h2))

story.append(
    P(
        "Automated PDF reports are generated for the available sectors."
    )
)

story.append(
    P(
        "<b>Current output:</b> 10 sector reports."
    )
)

story.append(
    P(
        "Sector reports are stored under "
        "<font name='Courier'>reports/sector/</font>."
    )
)

story.append(P("Portfolio Intelligence", h2))

for item in [
    "Total Companies",
    "Average Risk Score",
    "Average CFO Quality",
    "Average FCF Conversion",
    "Risk Distribution",
    "Highest Risk Company",
    "Lowest Risk Company",
]:
    story.append(B(item))

story.append(PageBreak())


# ============================================================
# PAGE 9 — API
# ============================================================

story.append(P("8. FastAPI Backend", h1))

story.append(
    P(
        "The FastAPI backend provides REST API endpoints for serving "
        "financial intelligence data to the Streamlit dashboard."
    )
)

story.append(P("Base URL", h2))

story.append(
    P(
        "<font name='Courier'>http://127.0.0.1:8000/api/v1</font>"
    )
)

story.append(P("Health endpoint", h2))

story.append(
    P(
        "<font name='Courier'>GET /api/v1/health</font>"
    )
)

story.append(P("Health response", h2))

story.append(
    P(
        "The health endpoint provides API status, database row counts, "
        "application uptime and API version."
    )
)

story.append(
    P(
        "<font name='Courier'>"
        '{"status": "ok", "version": "1.0.0"}'
        "</font>"
    )
)

story.append(P("Main API modules", h2))

for item in [
    "Health monitoring",
    "Company listing",
    "Company profiles",
    "Stock screening",
    "Sector analysis",
    "Peer groups",
    "Peer comparison",
    "Portfolio analysis",
    "Valuation",
    "Annual reports and documents",
]:
    story.append(B(item))

story.append(P("Dashboard integration", h2))

story.append(
    P(
        "The Streamlit dashboard communicates with the backend using "
        "src/dashboard/utils/api.py. The API client provides functions "
        "for health checks, company listing, company profiles, screener "
        "requests, sector data and companies by sector."
    )
)

story.append(PageBreak())


# ============================================================
# PAGE 10 — DATA QUALITY / TESTING
# ============================================================

story.append(P("9. Data Quality and Testing", h1))

story.append(P("Quality assurance coverage", h2))

for item in [
    "API endpoint validation",
    "Data validation",
    "Missing data handling",
    "Duplicate company detection",
    "Financial calculation validation",
    "Cash-flow validation",
    "CapEx intensity validation",
    "Risk score validation",
    "Pros & Cons validation",
    "Report generation",
    "Dashboard integration",
    "Multi-page navigation",
    "Screener testing",
    "Valuation testing",
    "CSV export testing",
    "Excel export testing",
    "ETL validation",
    "KPI validation",
]:
    story.append(B(item))

story.append(P("Data quality checks", h2))

for item in [
    "Duplicate company IDs",
    "Null company IDs",
    "Invalid foreign keys",
    "Invalid financial values",
    "Invalid stock prices",
    "Negative stock volume",
    "Invalid market capitalization",
    "Invalid P/E ratios",
]:
    story.append(B(item))

story.append(P("Automated test result", h2))

test_table = [
    ["Test Metric", "Result"],
    ["Total tests", "152"],
    ["Passed", "152"],
    ["Failed", "0"],
    ["Warnings", "2"],
    ["Overall", "PASS"],
]

table = Table(test_table, colWidths=[3.2 * inch, 2 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(table)

story.append(
    P(
        "Run the complete test suite with: "
        "<font name='Courier'>pytest -v</font>"
    )
)

story.append(PageBreak())


# ============================================================
# PAGE 11 — PERFORMANCE / TROUBLESHOOTING
# ============================================================

story.append(P("10. Performance and Troubleshooting", h1))

story.append(P("Documented performance results", h2))

performance = [
    ["Test", "Average", "Slowest", "Result"],
    ["Screener API", "0.042 sec", "0.052 sec", "PASS"],
    ["Company Profile API", "0.016 sec", "0.029 sec", "PASS"],
]

table = Table(performance, colWidths=[2.3 * inch, 1.2 * inch, 1.2 * inch, 1 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(table)

story.append(P("Troubleshooting: API does not start", h2))

for item in [
    "Confirm the virtual environment is activated.",
    "Confirm dependencies are installed.",
    "Run uvicorn src.api.main:app --reload.",
    "Check that port 8000 is available.",
]:
    story.append(B(item))

story.append(P("Troubleshooting: Dashboard does not load", h2))

for item in [
    "Confirm FastAPI is running.",
    "Confirm Streamlit is running.",
    "Run streamlit run src/dashboard/app.py.",
    "Open http://localhost:8501.",
    "Check the terminal for Python errors.",
]:
    story.append(B(item))

story.append(P("Troubleshooting: API data is unavailable", h2))

for item in [
    "Check the FastAPI health endpoint.",
    "Confirm the database is accessible.",
    "Check the API client configuration.",
    "Review the FastAPI terminal output.",
]:
    story.append(B(item))

story.append(PageBreak())


# ============================================================
# PAGE 12 — ANALYST WORKFLOW / OUTPUTS
# ============================================================

story.append(P("11. Recommended Analyst Workflow", h1))

workflow = [
    ("1", "Start FastAPI and Streamlit."),
    ("2", "Open the Home Dashboard."),
    ("3", "Review overall company and sector statistics."),
    ("4", "Use the Stock Screener to create a shortlist."),
    ("5", "Open individual Company Profiles."),
    ("6", "Review profitability, leverage and cash-flow indicators."),
    ("7", "Review historical trends."),
    ("8", "Compare the company with peers."),
    ("9", "Review the sector context."),
    ("10", "Review risk and valuation information."),
    ("11", "Read the generated Pros & Cons."),
    ("12", "Open the relevant company or sector PDF report."),
]

workflow_table = Table(
    [["Step", "Analyst Action"]] + workflow,
    colWidths=[0.7 * inch, 5.8 * inch],
)

workflow_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )
)

story.append(workflow_table)

story.append(P("Important output locations", h2))

for path in [
    "output/cashflow_intelligence.xlsx",
    "output/risk_scores.xlsx",
    "output/valuation_summary.xlsx",
    "output/peer_comparison.xlsx",
    "output/screener_output.xlsx",
    "output/pros_cons_generated.csv",
    "output/distress_alerts.csv",
    "output/capital_allocation.csv",
    "reports/sector/",
    "reports/tearsheets/",
    "reports/pytest_report.html",
]:
    story.append(
        P(f"<font name='Courier'>{path}</font>", small)
    )

story.append(PageBreak())


# ============================================================
# PAGE 13 — FINAL REFERENCE
# ============================================================

story.append(P("12. Quick Reference", h1))

quick = [
    ["Purpose", "Command / Location"],
    [
        "Start API",
        "uvicorn src.api.main:app --reload",
    ],
    [
        "Start Dashboard",
        "streamlit run src/dashboard/app.py",
    ],
    [
        "API",
        "http://127.0.0.1:8000",
    ],
    [
        "API Base",
        "http://127.0.0.1:8000/api/v1",
    ],
    [
        "Dashboard",
        "http://localhost:8501",
    ],
    [
        "Run Tests",
        "pytest -v",
    ],
    [
        "HTML Test Report",
        "reports/pytest_report.html",
    ],
    [
        "Company Reports",
        "reports/tearsheets/",
    ],
    [
        "Sector Reports",
        "reports/sector/",
    ],
]

table = Table(quick, colWidths=[2.1 * inch, 4.3 * inch])
table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
    )
)

story.append(table)

story.append(Spacer(1, 20))

story.append(P("Project Summary", h2))

story.append(
    P(
        "The N100 Financial Intelligence Platform combines financial "
        "data processing, financial ratios, valuation, risk intelligence, "
        "cash-flow analysis, capital allocation, peer comparison, "
        "sector analysis, stock screening and automated financial reporting."
    )
)

story.append(Spacer(1, 20))

story.append(
    P(
        "<b>Author:</b> Tamilarasan M<br/>"
        "Data Analyst | Data Science Enthusiast"
    )
)

doc.build(
    story,
    onFirstPage=footer,
    onLaterPages=footer,
)

print(f"Analyst guide generated: {OUTPUT}")