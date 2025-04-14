WITH monthly_equity_performance AS (
    -- Calculate monthly P&L for each equity fund
    SELECT 
        date_trunc('month',to_date("date",'MM/DD/YYYY')) AS month,
        name AS fund_name,
        SUM("REALISED P/L") AS monthly_pnl
    FROM external_funds
    WHERE "FINANCIAL TYPE" = 'Equities'
    GROUP BY month,fund_name
),
ranked_funds AS (
    -- Rank funds by monthly performance
    SELECT 
        month,
        fund_name,
        monthly_pnl,
        RANK() OVER (PARTITION BY month ORDER BY monthly_pnl DESC) AS performance_rank
    FROM monthly_equity_performance
),
best_funds AS (
    -- Select only the top performing fund each month
    SELECT 
        month,
        fund_name,
        monthly_pnl
    FROM ranked_funds
    WHERE performance_rank = 1
)
-- Calculate cumulative P&L for the best funds
SELECT 
    b.month,
    b.fund_name,
    b.monthly_pnl,
    SUM(b.monthly_pnl) OVER (
        PARTITION BY b.fund_name 
        ORDER BY b.month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_pnl
FROM best_funds b
ORDER BY b.month;
