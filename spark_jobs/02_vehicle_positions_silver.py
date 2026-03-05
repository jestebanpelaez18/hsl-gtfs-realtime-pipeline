from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, to_timestamp, to_date, current_timestamp
import os

JDBC_URL = os.getenv("WAREHOUSE_JDBC_URL", "jdbc:postgresql://warehouse-postgres:5432/hsl_db")
DB_USER = os.getenv("WAREHOUSE_DB_USER", "hsl_user")
DB_PASS = os.getenv("WAREHOUSE_DB_PASS", "hsl_pass")
DB_TABLE = "silver.vehicle_positions"

RAW_PATH = "/app/data/raw/vehicle_positions/*"

def main():
    spark = (
        SparkSession.builder
        .appName("HSL Vehicle Positions -> Silver")
        .getOrCreate()
    )

    df_raw = spark.read.json(RAW_PATH)

    # Your raw has: vehicle.timestamp as string unix seconds
    df = (
        df_raw
        .select(
            col("id").alias("raw_id"),

            col("vehicle.vehicle.id").alias("vehicle_id"),
            col("vehicle.trip.start_date").alias("trip_start_date"),
            col("vehicle.trip.start_time").alias("trip_start_time"),
            col("vehicle.trip.route_id").alias("route_id"),
            col("vehicle.trip.direction_id").alias("direction_id"),

            col("vehicle.position.latitude").cast("double").alias("latitude"),
            col("vehicle.position.longitude").cast("double").alias("longitude"),
            col("vehicle.position.speed").cast("double").alias("speed"),
            col("vehicle.position.bearing").cast("double").alias("bearing"),
            col("vehicle.stop_id").alias("stop_id"),

            col("vehicle.current_status").alias("current_status"),

            to_timestamp(from_unixtime(col("vehicle.timestamp").cast("long"))).alias("event_ts"),
        )
        .withColumn("event_date", to_date(col("event_ts")))
        .withColumn("ingestion_ts", current_timestamp())
    )

    # Basic safety: drop rows without keys we need
    df = df.dropna(subset=["vehicle_id", "event_ts", "latitude", "longitude"])

    df_out = df.select(
    "ingestion_ts",
    "event_ts",
    "event_date",
    "vehicle_id",
    "trip_start_date",
    "trip_start_time",
    "route_id",
    "direction_id",
    "latitude",
    "longitude",
    "speed",
    "bearing",
    "stop_id",
    "raw_id"
)

    # Write
    (df_out.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", DB_TABLE)
        .option("user", DB_USER)
        .option("password", DB_PASS)
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

    spark.stop()

if __name__ == "__main__":
    main()