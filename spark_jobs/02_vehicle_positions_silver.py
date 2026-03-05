from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lit, current_timestamp
from pyspark.sql.types import DoubleType

RAW_PATH = "/app/data/raw"  # dentro de Docker (volumen montado)
JDBC_URL = "jdbc:postgresql://warehouse-postgres:5432/hsl_db"
DBTABLE = "silver.vehicle_positions"

def main():
    spark = (
        SparkSession.builder
        .appName("HSL Vehicle Positions Silver")
        .getOrCreate()
    )

    df_raw = spark.read.json(f"{RAW_PATH}/*.json")

    df = (
        df_raw
        .selectExpr("explode(entity) as e")
        .select(
            col("e.id").alias("raw_id"),
            col("e.vehicle.timestamp").alias("event_unix_ts"),
            col("e.vehicle.trip.tripId").alias("trip_id"),
            col("e.vehicle.trip.routeId").alias("route_id"),
            col("e.vehicle.trip.directionId").alias("direction_id"),
            col("e.vehicle.vehicle.id").alias("vehicle_id"),
            col("e.vehicle.position.latitude").alias("latitude"),
            col("e.vehicle.position.longitude").alias("longitude"),
            col("e.vehicle.position.speed").alias("speed"),
            col("e.vehicle.position.bearing").alias("bearing"),
            col("e.vehicle.stopId").alias("stop_id"),
        )
    )

    df = (
        df.withColumn("ingestion_ts", current_timestamp())
          .withColumn("event_ts", to_timestamp(col("event_unix_ts").cast("timestamp")))
    )

    df = (
        df.withColumn("event_date", col("event_ts").cast("date"))
          .withColumn("latitude", col("latitude").cast(DoubleType()))
          .withColumn("longitude", col("longitude").cast(DoubleType()))
    )

    # Write in Postgres (append por ahora)
    (
        df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", DBTABLE)
        .option("user", "hsl_user")
        .option("password", "hsl_pass")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    )

    print("✅ Silver load completed")
    spark.stop()


if __name__ == "__main__":
    main()