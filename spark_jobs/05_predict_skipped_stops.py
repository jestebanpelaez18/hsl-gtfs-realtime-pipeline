from pyspark.sql import SparkSession
from pyspark.sql.functions import col, hour, dayofweek, round as spark_round
from pyspark.ml import PipelineModel
import os

JDBC_URL = os.getenv("WAREHOUSE_JDBC_URL", "jdbc:postgresql://warehouse-postgres:5432/hsl_db")
DB_USER = os.getenv("WAREHOUSE_DB_USER", "hsl_user")
DB_PASS = os.getenv("WAREHOUSE_DB_PASS", "hsl_pass")
MODEL_PATH = "/app/models/delay_prediction_model"

def main():
    spark = (
        SparkSession.builder
        .appName("HSL Skipped Stops Prediction")
        .getOrCreate()
    )

    print("Loading trained model...")
    model = PipelineModel.load(MODEL_PATH)

    print("Reading silver data...")
    df = ( 
    spark.read
    .format("jdbc")
    .option("url", JDBC_URL)
    .option("dbtable", """
        (SELECT * FROM silver.trip_updates 
         WHERE update_ts >= NOW() - INTERVAL '30 days') AS recent_updates
    """)
    .option("user", DB_USER)
    .option("password", DB_PASS)
    .option("driver", "org.postgresql.Driver")
    .load()
)

    print("Making predictions...")
    predictions = model.transform(df)

    # Extract probability of being SKIPPED (class 1)
    from pyspark.sql.functions import udf
    from pyspark.sql.types import DoubleType
    get_prob = udf(lambda v: float(v[1]), DoubleType())

    results = (
        predictions
        .withColumn("skip_probability", spark_round(get_prob(col("probability")), 4))
        .withColumn("predicted_skipped", col("prediction").cast("int"))
        .select(
            "event_date",
            "route_id",
            "direction_id",
            "stop_id",
            "hour_of_day",
            "day_of_week",
            "predicted_skipped",
            "skip_probability"
        )
        .filter(col("predicted_skipped") == 1)
        .orderBy(col("skip_probability").desc())
    )

    print(f"Total predicted skipped stops: {results.count()}")

    # Save to gold
    (
        results.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "gold.skipped_stops_predictions")
        .option("user", DB_USER)
        .option("password", DB_PASS)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print("Predictions saved to gold.skipped_stops_predictions")
    spark.stop()

if __name__ == "__main__":
    main()