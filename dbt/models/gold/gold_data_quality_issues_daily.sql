WITH vehicle_checks AS (
    SELECT
        event_date,
        COUNT(*)                                           AS total_records,
        SUM(CASE WHEN vehicle_id IS NULL THEN 1 ELSE 0 END) AS null_vehicle_id,
        SUM(CASE WHEN route_id IS NULL THEN 1 ELSE 0 END)   AS null_route_id,
        SUM(CASE WHEN latitude IS NULL 
             OR longitude IS NULL THEN 1 ELSE 0 END)        AS null_coordinates,
        SUM(CASE WHEN latitude < 59.9 
             OR latitude > 60.4
             OR longitude < 24.5
             OR longitude > 25.3 THEN 1 ELSE 0 END)         AS invalid_coordinates,
        SUM(CASE WHEN speed < 0 
             OR speed > 50 THEN 1 ELSE 0 END)               AS invalid_speed
    FROM silver.vehicle_positions
    WHERE event_date IS NOT NULL
    GROUP BY event_date
),

trip_checks AS (
    SELECT
        event_date,
        COUNT(*)                                            AS total_records,
        SUM(CASE WHEN route_id IS NULL THEN 1 ELSE 0 END)  AS null_route_id,
        SUM(CASE WHEN stop_id IS NULL THEN 1 ELSE 0 END)   AS null_stop_id,
        SUM(CASE WHEN update_ts IS NULL THEN 1 ELSE 0 END) AS null_update_ts,
        SUM(CASE WHEN arrival_ts > departure_ts THEN 1 ELSE 0 END) AS arrival_after_departure
    FROM silver.trip_updates
    WHERE event_date IS NOT NULL
    GROUP BY event_date
)

SELECT
    COALESCE(v.event_date, t.event_date)      AS event_date,

    v.total_records                            AS vp_total_records,
    v.null_vehicle_id                          AS vp_null_vehicle_id,
    v.null_route_id                            AS vp_null_route_id,
    v.null_coordinates                         AS vp_null_coordinates,
    v.invalid_coordinates                      AS vp_invalid_coordinates,
    v.invalid_speed                            AS vp_invalid_speed,

    t.total_records                            AS tu_total_records,
    t.null_route_id                            AS tu_null_route_id,
    t.null_stop_id                             AS tu_null_stop_id,
    t.null_update_ts                           AS tu_null_update_ts,
    t.arrival_after_departure                  AS tu_arrival_after_departure

FROM vehicle_checks v
FULL OUTER JOIN trip_checks t ON v.event_date = t.event_date
ORDER BY event_date