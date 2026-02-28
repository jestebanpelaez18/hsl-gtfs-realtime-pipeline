CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS silver.vehicle_positions (
  ingestion_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  event_ts TIMESTAMPTZ,
  event_date DATE,
  vehicle_id TEXT,
  trip_id TEXT,
  route_id TEXT,
  direction_id INT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  speed DOUBLE PRECISION,
  bearing DOUBLE PRECISION,
  stop_id TEXT,
  raw_id TEXT
);

CREATE TABLE IF NOT EXISTS silver.trip_updates (
  ingestion_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  event_ts TIMESTAMPTZ,
  event_date DATE,
  trip_id TEXT,
  route_id TEXT,
  stop_id TEXT,
  stop_sequence INT,
  arrival_delay_sec INT,
  departure_delay_sec INT,
  raw_id TEXT
);

-- Helpful indexes (basic)
CREATE INDEX IF NOT EXISTS idx_vp_event_date ON silver.vehicle_positions(event_date);
CREATE INDEX IF NOT EXISTS idx_tu_event_date ON silver.trip_updates(event_date);