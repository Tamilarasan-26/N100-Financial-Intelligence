# 📊 N100 Financial Intelligence Platform

A comprehensive financial analytics and intelligence platform for analyzing Nifty 100 companies.

The platform combines financial statement analysis, valuation, risk scoring, cash-flow intelligence, capital allocation analysis, peer comparison, sector analysis, stock screening, and automated financial reporting into a single system.

---

# 🚀 Key Features

- Multi-page Streamlit Financial Dashboard
- FastAPI Backend
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
- REST API Integration
- Automated API Testing
- Data Quality Testing
- Performance Testing
- End-to-End Integration Testing

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
├── db/
│   └── nifty100.db
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
│   ├── tearsheets/
│   ├── assets/
│   └── pytest_report.html
│
├── scripts/
│   ├── performance_test.py
│   ├── profile_performance_test.py
│   ├── profile_dashboard_performance.py
│   └── e2e_test.py
│
├── src/
│   ├── analytics/
│   │   ├── cagr.py
│   │   ├── capital_allocation.py
│   │   ├── capital_allocation_report.py
│   │   ├── cashflow_kpis.py
│   │   ├── clustering.py
│   │   ├── cluster_profiling.py
│   │   ├── correlation_analysis.py
│   │   ├── generate_cashflow.py
│   │   ├── outlier_detection.py
│   │   ├── pattern_changes.py
│   │   ├── peer.py
│   │   ├── peer_comparison.py
│   │   ├── populate_ratios.py
│   │   ├── portfolio_stats.py
│   │   ├── radar.py
│   │   ├── ratios.py
│   │   ├── risk_scoring.py
│   │   └── valuation.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── companies.py
│   │       ├── documents.py
│   │       ├── health.py
│   │       ├── peers.py
│   │       ├── portfolio.py
│   │       ├── screener.py
│   │       ├── sectors.py
│   │       └── valuation.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── __init__.py
│   │   ├── pages/
│   │   └── utils/
│   │       ├── api.py
│   │       ├── db.py
│   │       └── __init__.py
│   │
│   ├── etl/
│   │   ├── check_failures.py
│   │   ├── create_validated_data.py
│   │   ├── db_loader.py
│   │   ├── loader.py
│   │   ├── load_capital_allocation.py
│   │   ├── manual_review.py
│   │   ├── normaliser.py
│   │   ├── quarantine.py
│   │   ├── validator.py
│   │   └── verify_database.py
│   │
│   ├── nlp/
│   │   ├── parser.py
│   │   └── pros_cons_generator.py
│   │
│   ├── reports/
│   │   ├── generate_charts.py
│   │   ├── portfolio_charts.py
│   │   ├── portfolio_report.py
│   │   ├── portfolio_summary.py
│   │   ├── sector_report.py
│   │   └── tearsheet.py
│   │
│   └── screener/
│       ├── engine.py
│       └── __init__.py
│
├── tests/
│   ├── api/
│   │   ├── test_companies.py
│   │   ├── test_health.py
│   │   ├── test_peers.py
│   │   ├── test_screener.py
│   │   └── test_sectors.py
│   │
│   ├── dq/
│   │   └── test_rules.py
│   │
│   ├── etl/
│   │   ├── test_loader.py
│   │   ├── test_normaliser.py
│   │   └── test_validator.py
│   │
│   └── kpi/
│       ├── test_cagr.py
│       ├── test_leverage_efficiency.py
│       └── test_ratios.py
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

# ⚡ FastAPI Backend

The platform provides a FastAPI REST API for serving financial intelligence data to the Streamlit dashboard.

## API Base URL

```text
http://127.0.0.1:8000/api/v1
```

## Health Endpoint

```text
GET /api/v1/health
```

The health endpoint provides:

- API status
- Database row counts
- Application uptime
- API version

Example:

```json
{
    "status": "ok",
    "version": "1.0.0"
}
```

## Main API Modules

The backend provides endpoints for:

- Health monitoring
- Company listing
- Company profiles
- Stock screening
- Sector analysis
- Peer groups
- Peer comparison
- Portfolio analysis
- Valuation
- Annual reports and documents

---

# 🔌 Dashboard API Integration

The Streamlit dashboard communicates with the FastAPI backend using:

```text
src/dashboard/utils/api.py
```

The API client provides functions for:

- Health checks
- Company listing
- Company profiles
- Screener requests
- Sector data
- Companies by sector

The dashboard uses Streamlit caching to reduce repeated API requests.

The architecture is:

```text
┌─────────────────────────────┐
│    Streamlit Dashboard      │
│        Port 8501            │
└──────────────┬──────────────┘
               │
               │ HTTP Requests
               ▼
┌─────────────────────────────┐
│      FastAPI Backend        │
│        Port 8000            │
└──────────────┬──────────────┘
               │
               │ SQL Queries
               ▼
┌─────────────────────────────┐
│      SQLite Database        │
│       nifty100.db           │
└─────────────────────────────┘
```

---

# 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- FastAPI
- Uvicorn
- Plotly
- Matplotlib
- Scikit-learn
- SQLite
- OpenPyXL
- ReportLab
- Pytest
- Requests

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

# ▶️ Running the Application

The platform consists of two main services:

1. FastAPI backend
2. Streamlit dashboard

Both services should be running simultaneously.

## Start FastAPI

Open the first terminal inside the project directory.

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn src.api.main:app --reload
```

FastAPI will be available at:

```text
http://127.0.0.1:8000
```

API base URL:

```text
http://127.0.0.1:8000/api/v1
```

---

## Start Streamlit

Open a second terminal inside the project directory.

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run Streamlit:

```powershell
streamlit run src/dashboard/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

# 🧪 Quality Assurance

The project includes automated validation and testing for:

- API Endpoints
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
- ETL Validation
- KPI Validation

---

# 🧪 Automated Test Suite

The project uses Pytest for automated testing.

## API Tests

The API test suite covers:

- Health endpoint
- Company endpoints
- Screener endpoints
- Sector endpoints
- Peer endpoints

## Data Quality Tests

The data quality tests cover:

- Duplicate company IDs
- Null company IDs
- Invalid foreign keys
- Invalid financial values
- Invalid stock prices
- Negative volume
- Invalid market capitalization
- Invalid P/E ratios

## ETL Tests

The ETL test suite covers:

- Data loading
- Header validation
- Row count validation
- Company ID normalization
- Year normalization
- Column normalization
- Period normalization
- Validation failure detection

## KPI Tests

The KPI test suite covers:

- CAGR calculations
- Revenue CAGR
- PAT CAGR
- Debt-to-Equity
- Interest Coverage
- Net Debt
- Asset Turnover
- ROE
- ROCE
- ROA
- Operating Profit Margin
- Net Profit Margin
- Leverage flags

---

# 📊 Final Test Result

The complete automated test suite was executed successfully.

```text
Total tests : 152
Passed      : 152
Failed      : 0
Warnings    : 2
Result      : PASS
```

The final test execution completed successfully.

A detailed HTML test report is generated at:

```text
reports/pytest_report.html
```

---

# ⚡ Performance Testing

Performance testing was performed for the FastAPI backend and dashboard data-loading workflows.

## Screener API Performance

10 concurrent Screener API requests were tested.

```text
Successful requests : 10/10
Average response    : 0.042 seconds
Slowest response    : 0.052 seconds
Target              : 10 seconds
Result              : PASS
```

## Company Profile API Performance

Five company profiles were tested:

```text
TCS
INFY
RELIANCE
HDFCBANK
ICICIBANK
```

Results:

```text
Successful requests : 5/5
Average response    : 0.016 seconds
Slowest response    : 0.029 seconds
Target              : 3 seconds
Result              : PASS
```

---

# 🔄 End-to-End Integration Testing

The platform was tested with FastAPI and Streamlit running simultaneously.

## Service Checks

```text
FastAPI      : HTTP 200
Streamlit    : HTTP 200
```

## API Data Verification

```text
Health response structure : PASS
API status                : ok
Companies                 : 92
Financial ratios          : 1163
```

## Result

```text
PASS: FastAPI and Streamlit are running simultaneously
and API data is available.
```

---

# 🗄️ Database Performance Optimization

SQLite indexes were added to improve frequently used company/year queries.

## Financial Ratios

Index:

```text
idx_financial_ratios_company_year
```

Applied to:

```text
financial_ratios(company_id, year)
```

## Capital Allocation

Index:

```text
idx_capital_allocation_company_year
```

Applied to:

```text
capital_allocation(company_id, year)
```

These indexes improve query performance for company-specific and year-specific financial analysis.

---

# 🩺 API Health Monitoring

The API health endpoint provides information about:

- API status
- Database row counts
- API version
- Application uptime

Current database statistics include:

```text
Companies          : 92
Financial Ratios   : 1163
Market Cap         : 552
Stock Prices       : 5520
```

---

# 🧪 Running Tests

Run the complete test suite:

```powershell
pytest -v
```

Generate the HTML test report:

```powershell
pytest -v --html=reports/pytest_report.html
```

---

# ⚡ Running Performance Tests

## Screener API Performance

```powershell
python scripts/performance_test.py
```

## Company Profile Performance

```powershell
python scripts/profile_performance_test.py
```

## Dashboard Profile Performance

```powershell
python scripts/profile_dashboard_performance.py
```

## End-to-End Integration Test

```powershell
python scripts/e2e_test.py
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

## Test Reports

```text
reports/pytest_report.html
```

---

# 🧪 Final Core Data Validation

```text
Risk rows: 92
Cash-flow rows: 92

Risk companies: 92
Cash-flow companies: 92
```

## Risk Distribution

```text
LOW    : 52
MEDIUM : 19
HIGH   : 21
```

## Cash-Flow Validation

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

A financial analytics platform combining financial data, valuation, risk intelligence, cash-flow analysis, capital allocation analysis, peer comparison, sector analysis, stock screening, and automated financial reporting.