DROP VIEW IF EXISTS vw_ab_test_member_web;
CREATE VIEW vw_ab_test_member_web AS
SELECT
    s.fence_id,
    s.variant,
    s.mechanic,
    COUNT(s.session_id) AS sessions,
    SUM(s.converted) AS bookings,
    ROUND(CAST(SUM(s.converted) AS REAL) / COUNT(s.session_id), 5) AS conversion_rate,
    ROUND(SUM(s.gbv), 2) AS gbv,
    ROUND(SUM(s.promo_cost), 2) AS promo_cost,
    ROUND(SUM(s.contribution), 2) AS contribution,
    ROUND(AVG(s.contribution), 4) AS contribution_per_session,
    ROUND(
        CAST(SUM(s.cancelled) AS REAL) / NULLIF(SUM(s.converted), 0),
        4
    ) AS cancel_rate
FROM fact_sessions s
JOIN dim_fence f ON f.fence_id = s.fence_id
WHERE s.fence_id = 'member_web'
  AND s.variant IN ('control_cash', 'treatment_points')
GROUP BY s.fence_id, s.variant, s.mechanic;
