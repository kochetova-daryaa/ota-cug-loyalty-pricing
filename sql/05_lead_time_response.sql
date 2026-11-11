DROP VIEW IF EXISTS vw_lead_time_response;
CREATE VIEW vw_lead_time_response AS
SELECT
    s.fence_id,
    s.lead_bucket,
    COUNT(s.session_id) AS sessions,
    SUM(s.converted) AS bookings,
    ROUND(CAST(SUM(s.converted) AS REAL) / COUNT(s.session_id), 4) AS conversion_rate,
    ROUND(
        CAST(SUM(s.cannibalized) AS REAL) / NULLIF(SUM(s.converted), 0),
        4
    ) AS cannibalization_share,
    ROUND(AVG(s.cug_price_index), 4) AS avg_cug_price_index,
    ROUND(SUM(s.contribution), 2) AS contribution
FROM fact_sessions s
JOIN dim_fence f ON f.fence_id = s.fence_id
GROUP BY s.fence_id, s.lead_bucket;
