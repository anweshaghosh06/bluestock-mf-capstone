-- =====================================================
-- Q1: Top 5 fund houses by total AUM
-- =====================================================

SELECT
    fund_house,
    ROUND(SUM(aum_cr),2) AS total_aum_cr
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum_cr DESC
LIMIT 5;


-- =====================================================
-- Q2: Average NAV per month
-- =====================================================

SELECT
    f.scheme_name,
    STRFTIME('%Y-%m', n.date_id) AS month,
    ROUND(AVG(n.nav),4) AS avg_nav
FROM fact_nav n
JOIN dim_fund f
ON n.amfi_code = f.amfi_code
GROUP BY f.scheme_name, month
ORDER BY f.scheme_name, month;


-- =====================================================
-- Q3: SIP inflow YoY growth
-- =====================================================

WITH yearly_sip AS (
    SELECT
        STRFTIME('%Y', date_id) AS year,
        SUM(amount_inr) AS total_sip
    FROM fact_transactions
    WHERE transaction_type='SIP'
    GROUP BY year
)

SELECT
    year,
    ROUND(total_sip,2) AS total_sip,
    ROUND(
        (
            total_sip -
            LAG(total_sip) OVER(ORDER BY year)
        ) * 100.0 /
        LAG(total_sip) OVER(ORDER BY year),
        2
    ) AS yoy_pct
FROM yearly_sip;


-- =====================================================
-- Q4: Transactions by state
-- =====================================================

SELECT
    state,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount_inr),2) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY txn_count DESC;


-- =====================================================
-- Q5: Expense ratio below 1%
-- =====================================================

SELECT
    f.scheme_name,
    f.fund_house,
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f
ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1
ORDER BY p.expense_ratio_pct;


-- =====================================================
-- Q6: Best funds by 3Y return
-- =====================================================

SELECT
    f.scheme_name,
    f.category,
    ROUND(p.return_3yr_pct,2) AS return_3yr_pct
FROM fact_performance p
JOIN dim_fund f
ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct IS NOT NULL
ORDER BY p.return_3yr_pct DESC
LIMIT 10;


-- =====================================================
-- Q7: Monthly redemption volume
-- =====================================================

SELECT
    STRFTIME('%Y-%m', date_id) AS month,
    COUNT(*) AS redemptions,
    ROUND(SUM(amount_inr),2) AS total_redeemed
FROM fact_transactions
WHERE transaction_type='Redemption'
GROUP BY month
ORDER BY month;


-- =====================================================
-- Q8: Highest Sharpe ratio
-- =====================================================

SELECT
    f.scheme_name,
    ROUND(p.sharpe_ratio,3) AS sharpe_ratio
FROM fact_performance p
JOIN dim_fund f
ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 5;


-- =====================================================
-- Q9: KYC distribution
-- =====================================================

SELECT
    kyc_status,
    COUNT(*) AS count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM fact_transactions),
        2
    ) AS pct
FROM fact_transactions
GROUP BY kyc_status;


-- =====================================================
-- Q10: NAV growth %
-- =====================================================

SELECT
    f.scheme_name,
    ROUND(
        (MAX(n.nav)-MIN(n.nav))
        *100.0/
        MIN(n.nav),
        2
    ) AS nav_growth_pct
FROM fact_nav n
JOIN dim_fund f
ON n.amfi_code = f.amfi_code
GROUP BY f.scheme_name
ORDER BY nav_growth_pct DESC;