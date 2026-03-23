WITH trip_updates AS (
    SELECT
        event_date,
        route_id,
        direction_id,
        stop_id,
        arrival_ts,
        departure_ts,
        trip_start_time,
        arrival_uncertainty,
        departure_uncertainty
    FROM {{ source('silver', 'trip_updates') }}
    WHERE event_date IS NOT NULL
      AND route_id IS NOT NULL
)

SELECT
    event_date,
    route_id,
    direction_id,
    COUNT(*)                        AS total_stop_updates,
    COUNT(DISTINCT stop_id)         AS unique_stops,
    MIN(arrival_ts)                 AS first_arrival_ts,
    MAX(arrival_ts)                 AS last_arrival_ts,
    AVG(arrival_uncertainty)        AS avg_arrival_uncertainty,
    AVG(departure_uncertainty)      AS avg_departure_uncertainty
FROM trip_updates
GROUP BY event_date, route_id, direction_id