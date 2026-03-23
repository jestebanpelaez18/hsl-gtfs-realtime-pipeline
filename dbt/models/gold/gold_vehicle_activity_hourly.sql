WITH vehicle_positions AS (
    SELECT
        event_date,
        route_id,
        direction_id,
        vehicle_id,
        event_ts,
        speed,
        latitude,
        longitude
    FROM {{ source('silver', 'vehicle_positions') }}
    WHERE event_date IS NOT NULL
      AND route_id IS NOT NULL
      AND vehicle_id IS NOT NULL
)

SELECT
    event_date,
    EXTRACT(HOUR FROM event_ts)::INT     AS hour_of_day,
    route_id,
    direction_id,
    COUNT(DISTINCT vehicle_id)           AS active_vehicles,
    COUNT(*)                             AS total_position_updates,
    AVG(speed)                           AS avg_speed_ms,
    MIN(speed)                           AS min_speed_ms,
    MAX(speed)                           AS max_speed_ms
FROM vehicle_positions
GROUP BY event_date, EXTRACT(HOUR FROM event_ts), route_id, direction_id
ORDER BY event_date, hour_of_day, route_id