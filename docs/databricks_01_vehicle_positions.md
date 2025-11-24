# Databricks Notebook: Vehicle Positions Silver

This notebook was originally developed and executed on **Databricks Free Edition**
using PySpark. It performs the following steps:

1. Reads a GTFS-Realtime `vehicle_positions` JSON export.
2. Extracts nested fields from the `vehicle` struct
   (`vehicle_id`, `route_id`, `lat`, `lon`, `speed`, raw timestamp).
3. Converts the raw UNIX timestamp into a proper Spark `timestamp` (`event_ts`).
4. Adds partition columns `event_date` and `event_hour`.
5. Writes the cleaned data to a Delta table:
   `hsl_demo.vehicle_positions_silver`.

For local execution (VSCode / Jupyter), a helper cell at the top of the
notebook shows how to create a local Spark session and use a local file path.
