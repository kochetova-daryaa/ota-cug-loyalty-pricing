DROP VIEW IF EXISTS vw_fence_scorecard;
CREATE VIEW vw_fence_scorecard AS
SELECT
    f.fence_id,
    f.mechanic_now,
    f.nominal_rate_now,
    COUNT(s.session_id) AS sessions,
    SUM(s.converted) AS bookings,
    CAST(SUM(s.converted) AS REAL) / COUNT(s.session_id) AS conversion_rate,
    ROUND(SUM(s.gbv), 2) AS gbv,
    ROUND(SUM(s.net_revenue_before_promo), 2) AS net_revenue_before_promo,
    ROUND(SUM(s.promo_cost), 2) AS promo_cost,
    ROUND(SUM(s.cannibalized_promo_cost), 2) AS cannibalized_promo_cost,
    ROUND(
        CAST(SUM(s.cannibalized) AS REAL) / NULLIF(SUM(s.converted), 0),
        4
    ) AS cannibalization_share,
    ROUND(SUM(s.contribution), 2) AS contribution,
    ROUND(AVG(s.contribution), 4) AS contribution_per_session,
    ROUND(
        SUM(s.contribution) / SUM(SUM(s.contribution)) OVER (),
        4
    ) AS share_of_total_contribution
FROM fact_sessions s
JOIN dim_fence f ON f.fence_id = s.fence_id
GROUP BY f.fence_id, f.mechanic_now, f.nominal_rate_now;
