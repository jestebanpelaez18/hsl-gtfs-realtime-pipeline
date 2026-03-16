from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_unixtime,
    to_timestamp,
    to_date,
    current_timestamp,
    explode
)
import os
import psycopg2

JDBC_URL = os.getenv("WAREHOUSE_JDBC_URL", "jdbc:postgresql://warehouse-postgres:5432/hsl_db")
DB_USER = os.getenv("WAREHOUSE_DB_USER", "hsl_user")
DB_PASS = os.getenv("WAREHOUSE_DB_PASS", "hsl_pass")
DB_TABLE = "silver.trip_updates"

RAW_PATH = "/app/data/raw/trip_updates/*.jsonl"

def main():
    spark = (
        SparkSession.builder
        .appName("HSL Trip Updates -> Silver")
        .getOrCreate()
    )

    df_raw = spark.read.json(RAW_PATH)

    df = (
        df_raw
        .withColumn("stu", explode(col("trip_update.stop_time_update")))
        .select(
            col("id").alias("raw_id"),

            col("trip_update.trip.start_date").alias("trip_start_date"),
            col("trip_update.trip.start_time").alias("trip_start_time"),
            col("trip_update.trip.route_id").alias("route_id"),
            col("trip_update.trip.direction_id").alias("direction_id"),
            col("trip_update.trip.schedule_relationship").alias("trip_schedule_relationship"),

            col("stu.stop_id").alias("stop_id"),
            col("stu.schedule_relationship").alias("stop_schedule_relationship"),

            col("stu.arrival.time").cast("long").alias("arrival_unix_ts"),
            col("stu.departure.time").cast("long").alias("departure_unix_ts"),

            col("stu.arrival.uncertainty").cast("int").alias("arrival_uncertainty"),
            col("stu.departure.uncertainty").cast("int").alias("departure_uncertainty"),

            col("trip_update.timestamp").cast("long").alias("update_unix_ts")
        )
        .withColumn("arrival_ts", to_timestamp(from_unixtime(col("arrival_unix_ts"))))
        .withColumn("departure_ts", to_timestamp(from_unixtime(col("departure_unix_ts"))))
        .withColumn("update_ts", to_timestamp(from_unixtime(col("update_unix_ts"))))
        .withColumn("event_date", to_date(col("update_ts")))
        .withColumn("ingestion_ts", current_timestamp())
    )

    df = df.dropna(subset=["route_id", "stop_id", "update_ts"])

    df_out = df.select(
        "ingestion_ts",
        "update_ts",
        "event_date",
        "trip_start_date",
        "trip_start_time",
        "route_id",
        "direction_id",
        "trip_schedule_relationship",
        "stop_id",
        "stop_schedule_relationship",
        "arrival_ts",
        "departure_ts",
        "arrival_uncertainty",
        "departure_uncertainty",
        "raw_id"
    )


    # Get the dates present in this batch
    dates = [row.event_date for row in df_out.select("event_date").distinct().collect()]

    # Delete existing data for those dates before inserting (idempotency)
    conn = psycopg2.connect(
        host="warehouse-postgres",
        port=5432,
        dbname="hsl_db",
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()
    for date in dates:
        cursor.execute(f"DELETE FROM {DB_TABLE} WHERE event_date = %s", (date,))
    conn.commit()
    cursor.close()
    conn.close()

    # Now insert fresh data
    (
        df_out.write
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