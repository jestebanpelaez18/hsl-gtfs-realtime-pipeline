from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, col

spark = SparkSession.builder.appName("HSL Silver Loader").getOrCreate()

data = [
    ("2025-01-01 10:00:00", "2025-01-01", "vehicle_1", "trip_1", "route_55", 60.192059, 24.945831)
]

columns = ["event_ts", "event_date", "vehicle_id", "trip_id", "route_id", "latitude", "longitude"]

df = spark.createDataFrame(data, columns)

df = (
    df.withColumn("event_ts", to_timestamp(col("event_ts"), "yyyy-MM-dd HH:mm:ss"))
      .withColumn("event_date", col("event_date").cast("date"))
      .withColumn("latitude", col("latitude").cast("double"))
      .withColumn("longitude", col("longitude").cast("double"))
)

jdbc_url = "jdbc:postgresql://warehouse-postgres:5432/hsl_db"

(
    df.write
    .format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", "silver.vehicle_positions")
    .option("user", "hsl_user")
    .option("password", "hsl_pass")
    .option("driver", "org.postgresql.Driver")
    .mode("append")
    .save()
)

print("Write completed.")
spark.stop()