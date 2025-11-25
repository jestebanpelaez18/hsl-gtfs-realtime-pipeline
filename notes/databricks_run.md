# Databricks Run Guide

- Import `notebooks/01_read_raw_vehicle_positions`.
- Configure cluster (small is fine). 
- Set input path to raw JSON exports (GTFS-RT).
- Execute notebook; the job writes a partitioned Parquet/Delta dataset.
- Validate by reading back and sampling records.

Notes:
- All timestamps are handled in UTC for consistency.
- Schema evolution is handled at the notebook level.
