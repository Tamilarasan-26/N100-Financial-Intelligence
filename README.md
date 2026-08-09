# 📊 N100 Financial Intelligence Platform

A comprehensive financial analytics and intelligence platform for analyzing Nifty 100 companies.

The platform combines financial statement analysis, valuation, risk scoring, cash-flow intelligence, capital allocation analysis, peer comparison, sector analysis, stock screening, and automated financial reporting into a single system.

---

# 🚀 Key Features

- Multi-page Streamlit Financial Dashboard
- Company Profile Analysis
- Financial Stock Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation Analysis
- Cash-Flow Intelligence
- Risk Scoring
- Financial Distress Detection
- Automated Pros & Cons Generation
- Company Tearsheet Generation
- Sector Report Generation
- Portfolio Summary
- Portfolio Risk & Allocation Charts
- Valuation Analysis
- Annual Report Viewer
- CSV & Excel Exports
- Interactive Plotly Visualizations
- SQLite Database Integration

---

# 🏗️ Project Architecture

```text
N100_FINANCIAL_INTELLIGENCE/
│
├── config/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
│
├── output/
│   ├── cashflow_intelligence.xlsx
│   ├── risk_scores.xlsx
│   ├── valuation_summary.xlsx
│   ├── peer_comparison.xlsx
│   ├── screener_output.xlsx
│   ├── pros_cons_generated.csv
│   ├── distress_alerts.csv
│   ├── capital_allocation.csv
│   └── ...
│
├── reports/
│   ├── charts/
│   ├── sector/
│   └── tearsheets/
│
├── src/
│   ├── analytics/
│   │   ├── cagr.py
│   │   ├── capital_allocation.py
│   │   ├── capital_allocation_report.py
│   │   ├── cashflow_kpis.py
│   │   ├── generate_cashflow.py
│   │   ├── pattern_changes.py
│   │   ├── peer.py
│   │   ├── peer_comparison.py
│   │   ├── populate_ratios.py
│   │   ├── radar.py
│   │   ├── ratios.py
│   │   ├── risk_scoring.py
│   │   └── valuation.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   └── utils/
│   │
│   ├── nlp/
│   │   └── pros_cons_generator.py
│   │
│   ├── reports/
│   │   ├── tearsheet.py
│   │   ├── sector_report.py
│   │   ├── portfolio_summary.py
│   │   ├── portfolio_charts.py
│   │   └── portfolio_report.py
│   │
│   └── screener/
│
├── README.md
└── requirements.txt
```

---

# 🧮 Financial Intelligence

## Cash-Flow Intelligence

The platform analyzes company cash-flow behavior using:

- Operating Cash Flow
- Free Cash Flow
- CFO Quality
- CapEx Intensity
- FCF Conversion
- Capital Allocation
- Deleveraging
- Financial Distress

### Key Formulas

```text
FCF = CFO - CapEx
CFO Quality = CFO / Net Profit
CapEx Intensity = CapEx / Sales × 100
FCF Conversion = FCF / Net Profit × 100
```

---

# ⚠️ Risk Intelligence

The platform generates financial risk scores for analyzed companies.

## Current Risk Distribution

| Risk Category | Companies |
|---|---:|
| LOW | 52 |
| MEDIUM | 19 |
| HIGH | 21 |
| **Total** | **92** |

The system also identifies companies requiring financial distress attention.

### Current Distress Alerts

```text
13 Companies
```

---

# 🧠 Pros & Cons Intelligence

The platform automatically generates financial strengths and weaknesses using rule-based financial analysis.

The rules evaluate metrics including:

- Return on Equity
- Debt-to-Equity
- Free Cash Flow
- Operating Profit Margin
- Interest Coverage
- Asset Turnover
- Cash from Operations
- Earnings Per Share
- Book Value Per Share
- Dividend Payout
- Net Profit Margin
- Total Debt

## Current Output

```text
Companies Analyzed: 92
Pros & Cons Generated: 856
Companies with Pros: 92
Companies with Cons: 92
```

---

# 📑 Automated Financial Reporting

## Company Tearsheets

The platform automatically generates a financial PDF tearsheet for each analyzed company.

### Current Output

```text
Total Companies   : 92
Generated Reports : 92
Skipped Reports   : 0
Failed Reports    : 0
```

Reports are stored in:

```text
reports/tearsheets/
```

---

## Sector Reports

The platform generates automated PDF reports for all available sectors.

### Current Sectors

1. Communication Services
2. Consumer Discretionary
3. Consumer Staples
4. Energy
5. Financials
6. Healthcare
7. Industrials
8. Information Technology
9. Materials
10. Real Estate

### Current Output

```text
Sector Reports: 10
```

Reports are stored in:

```text
reports/sector/
```

---

# 📊 Portfolio Intelligence

The platform provides portfolio-level analysis across the 92 companies.

## Portfolio Summary

The portfolio report includes:

- Total Companies
- Average Risk Score
- Average CFO Quality
- Average FCF Conversion
- Risk Distribution
- Highest Risk Company
- Lowest Risk Company

## Portfolio Charts

The platform generates:

1. Portfolio Risk Distribution
2. Portfolio Capital Allocation
3. Portfolio Sector Distribution
4. Top 10 Highest Risk Companies
5. Top 10 Lowest Risk Companies

Charts are stored in:

```text
reports/charts/
```

---

# 📈 Streamlit Dashboard

The project provides an interactive multi-page Streamlit dashboard.

## 1. Home Dashboard

Displays:

- Total Companies
- Average ROE
- Average P/E
- Average D/E
- Revenue CAGR
- Debt-Free Companies
- Sector Distribution

## 2. Company Profile

Displays:

- Company Information
- Financial Ratios
- Profit & Loss
- Balance Sheet
- Cash Flow
- Revenue Trends
- ROE vs ROCE Trends
- Pros & Cons

## 3. Stock Screener

Features:

- Custom Metric Filters
- Preset Filters
- Financial Screening
- Live Results
- CSV Download

## 4. Peer Comparison

Displays:

- KPI Comparison
- Sector Average
- Company Metrics

## 5. Trend Analysis

Displays:

- Multi-Metric Trend Charts
- Growth Percentage Labels
- Historical Financial Trends

## 6. Sector Analysis

Displays:

- Sector Bubble Chart
- Sector KPI Analysis
- Sector Comparison

## 7. Capital Allocation Map

Displays:

- Capital Allocation Treemap
- Company Distribution by Allocation Pattern

## 8. Annual Reports

Provides:

- Company-wise Annual Reports
- PDF Report Links

---

# 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Matplotlib
- Scikit-learn
- SQLite
- OpenPyXL
- ReportLab

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd N100_FINANCIAL_INTELLIGENCE
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

## 3. Activate the Virtual Environment

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Dashboard

```bash
streamlit run src/dashboard/app.py
```

---

# 📁 Important Output Files

## Excel Outputs

```text
output/cashflow_intelligence.xlsx
output/risk_scores.xlsx
output/valuation_summary.xlsx
output/peer_comparison.xlsx
output/screener_output.xlsx
```

## CSV Outputs

```text
output/pros_cons_generated.csv
output/distress_alerts.csv
output/capital_allocation.csv
output/capital_allocation_summary.csv
output/risk_summary.csv
output/valuation_flags.csv
```

## PDF Reports

```text
reports/sector/
reports/tearsheets/
```

---

# 🧪 Quality Assurance

The project includes validation and testing for:

- Data Validation
- Missing Data Handling
- Duplicate Company Detection
- Financial Calculation Validation
- Cash-Flow Validation
- CapEx Intensity Validation
- Risk Score Validation
- Pros & Cons Validation
- Report Generation
- Dashboard Integration
- Multi-Page Navigation
- Screener Testing
- Valuation Testing
- CSV Export Testing
- Excel Export Testing

## Final Core Data Validation

```text
Risk rows: 92
Cash-flow rows: 92

Risk companies: 92
Cash-flow companies: 92
```

### Risk Distribution

```text
LOW    : 52
MEDIUM : 19
HIGH   : 21
```

### Cash-Flow Validation

```text
Companies: 92
Negative CapEx intensity: 0
Missing CapEx intensity: 0
Distress flags: 13
```

---

# 📊 Project Scale

The completed platform currently contains:

```text
92 Companies
10 Sectors
92 Company Tearsheet Reports
10 Sector Reports
1 Portfolio Summary Report
5 Portfolio-Level Charts
856 Financial Pros & Cons
13 Distress Alerts
```

---

# 🔮 Future Enhancements

- Live NSE/BSE Market Data Integration
- User Authentication
- Portfolio Tracking
- AI-Based Stock Recommendation
- LLM-Powered Financial Research Assistant
- Automated Financial News Sentiment Analysis
- Real-Time Financial Alerts
- Advanced Portfolio Optimization
- Cloud Deployment

---

# 👨‍💻 Author

**Tamilarasan M**

Data Analyst | Data Science Enthusiast

**N100 Financial Intelligence Platform**

A financial analytics platform combining financial data, valuation, risk intelligence, cash-flow analysis, capital allocation analysis, and automated financial reporting.