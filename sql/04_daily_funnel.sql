DROP VIEW IF EXISTS vw_daily_funnel;
CREATE VIEW vw_daily_funnel AS
WITH daily AS (
    SELECT
        s.session_date,
        s.fence_id,
        COUNT(s.session_id) AS sessions,
        SUM(s.converted) AS bookings,
        ROUND(SUM(s.gbv), 2) AS gbv,
        ROUND(SUM(s.promo_cost), 2) AS promo_cost,
        ROUND(SUM(s.contribution), 2) AS contribution
    FROM fact_sessions s
    JOIN dim_fence f ON f.fence_id = s.fence_id
    GROUP BY s.session_date, s.fence_id
)
SELECT
    session_date,
    fence_id,
    sessions,
    bookings,
    CAST(bookings AS REAL) / sessions AS conversion_rate,
    gbv,
    promo_cost,
    contribution,
    ROUND(
        AVG(contribution) OVER (
            PARTITION BY fence_id
            ORDER BY session_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS contribution_7d_ma,
    ROUND(
        LAG(contribution, 7) OVER (
            PARTITION BY fence_id
            ORDER BY session_date
        ),
        2
    ) AS contribution_lag_7d
FROM daily;
