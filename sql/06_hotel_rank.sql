DROP VIEW IF EXISTS vw_hotel_rank;
CREATE VIEW vw_hotel_rank AS
WITH hotel_totals AS (
    SELECT
        h.hotel_id,
        h.hotel_name,
        h.city,
        h.stars,
        COUNT(s.session_id) AS sessions,
        SUM(s.converted) AS bookings,
        ROUND(SUM(s.gbv), 2) AS gbv,
        ROUND(SUM(s.promo_cost), 2) AS promo_cost,
        ROUND(SUM(s.contribution), 2) AS contribution
    FROM fact_sessions s
    JOIN dim_hotel h ON h.hotel_id = s.hotel_id
    GROUP BY h.hotel_id, h.hotel_name, h.city, h.stars
)
SELECT
    hotel_id,
    hotel_name,
    city,
    stars,
    sessions,
    bookings,
    gbv,
    promo_cost,
    contribution,
    RANK() OVER (PARTITION BY city ORDER BY contribution DESC) AS city_rank,
    ROUND(
        contribution / SUM(contribution) OVER (PARTITION BY city),
        4
    ) AS city_contribution_share
FROM hotel_totals;
