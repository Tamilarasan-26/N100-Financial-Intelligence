-- N100 FINANCIAL INTELLIGENCE PLATFORM
-- Sprint 1 - Exploratory SQL Queries

-- Query 1: Top 10 companies by market capitalization

SELECT
    c.id,
    c.company_name,
    m.year,
    m.market_cap_crore
FROM companies c
JOIN market_cap m
    ON c.id = m.company_id
ORDER BY m.market_cap_crore DESC
LIMIT 10;


-- Query 2: Average ROE by sector

SELECT
    c.broad_sector,
    ROUND(AVG(f.return_on_equity_pct), 2) AS average_roe
FROM companies c
JOIN financial_ratios f
    ON c.id = f.company_id
GROUP BY c.broad_sector
ORDER BY average_roe DESC;


-- Query 3: Companies with highest net profit

SELECT
    c.company_name,
    p.year,
    p.net_profit
FROM companies c
JOIN profitandloss p
    ON c.id = p.company_id
ORDER BY p.net_profit DESC
LIMIT 10;


-- Query 4: Companies with high debt-to-equity ratio

SELECT
    c.company_name,
    f.year,
    f.debt_to_equity
FROM companies c
JOIN financial_ratios f
    ON c.id = f.company_id
WHERE f.debt_to_equity > 2
ORDER BY f.debt_to_equity DESC;


-- Query 5: Sector-wise company distribution

SELECT
    broad_sector,
    COUNT(*) AS company_count
FROM companies
GROUP BY broad_sector
ORDER BY company_count DESC;


-- Query 6: Top companies by operating profit margin

SELECT
    c.company_name,
    p.year,
    p.opm_percentage
FROM companies c
JOIN profitandloss p
    ON c.id = p.company_id
ORDER BY p.opm_percentage DESC
LIMIT 10;


-- Query 7: Average closing stock price by company

SELECT
    c.company_name,
    ROUND(AVG(s.close_price), 2) AS average_close_price
FROM companies c
JOIN stock_prices s
    ON c.id = s.company_id
GROUP BY c.id, c.company_name
ORDER BY average_close_price DESC
LIMIT 10;


-- Query 8: Companies with negative net cash flow

SELECT
    c.company_name,
    cf.year,
    cf.net_cash_flow
FROM companies c
JOIN cashflow cf
    ON c.id = cf.company_id
WHERE cf.net_cash_flow < 0
ORDER BY cf.net_cash_flow ASC;


-- Query 9: Average PE ratio by sector

SELECT
    c.broad_sector,
    ROUND(AVG(m.pe_ratio), 2) AS average_pe_ratio
FROM companies c
JOIN market_cap m
    ON c.id = m.company_id
GROUP BY c.broad_sector
ORDER BY average_pe_ratio DESC;


-- Query 10: Financial summary by company

SELECT
    c.company_name,
    c.broad_sector,
    ROUND(AVG(f.return_on_equity_pct), 2) AS avg_roe,
    ROUND(AVG(f.debt_to_equity), 2) AS avg_debt_equity,
    ROUND(AVG(f.interest_coverage), 2) AS avg_interest_coverage
FROM companies c
JOIN financial_ratios f
    ON c.id = f.company_id
GROUP BY c.id, c.company_name, c.broad_sector
ORDER BY avg_roe DESC;