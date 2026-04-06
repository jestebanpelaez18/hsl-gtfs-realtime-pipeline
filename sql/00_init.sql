CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS silver.vehicle_positions (
  ingestion_ts    TIMESTAMPTZ,
  event_ts        TIMESTAMPTZ,
  event_date      DATE,
  vehicle_id      TEXT,
  trip_start_date TEXT,
  trip_start_time TEXT,
  route_id        TEXT,
  direction_id    INT,
  latitude        DOUBLE PRECISION,
  longitude       DOUBLE PRECISION,
  speed           DOUBLE PRECISION,
  bearing         DOUBLE PRECISION,
  stop_id         TEXT,
  raw_id          TEXT
);

CREATE TABLE IF NOT EXISTS silver.trip_updates (
  ingestion_ts              TIMESTAMPTZ,
  update_ts                 TIMESTAMPTZ,
  event_date                DATE,
  trip_start_date           TEXT,
  trip_start_time           TEXT,
  route_id                  TEXT,
  direction_id              INT,
  trip_schedule_relationship TEXT,
  stop_id                   TEXT,
  stop_schedule_relationship TEXT,
  arrival_ts                TIMESTAMPTZ,
  departure_ts              TIMESTAMPTZ,
  arrival_uncertainty       INT,
  departure_uncertainty     INT,
  raw_id                    TEXT
);

CREATE INDEX IF NOT EXISTS idx_vp_event_date ON silver.vehicle_positions(event_date);
CREATE INDEX IF NOT EXISTS idx_tu_event_date ON silver.trip_updates(event_date);

CREATE TABLE IF NOT EXISTS gold.ml_model_results (
    run_ts          TIMESTAMPTZ DEFAULT now(),
    auc_score       DOUBLE PRECISION,
    train_size      BIGINT,
    test_size       BIGINT
);

CREATE TABLE IF NOT EXISTS gold.skipped_stops_predictions (
    event_date          DATE,
    route_id            TEXT,
    direction_id        INT,
    stop_id             TEXT,
    hour_of_day         INT,
    day_of_week         INT,
    predicted_skipped   INT,
    skip_probability    DOUBLE PRECISION
);