from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, hour, dayofweek, when
)
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline
import os

JDBC_URL = os.getenv("WAREHOUSE_JDBC_URL", "jdbc:postgresql://warehouse-postgres:5432/hsl_db")
DB_USER = os.getenv("WAREHOUSE_DB_USER", "hsl_user")
DB_PASS = os.getenv("WAREHOUSE_DB_PASS", "hsl_pass")

def read_silver(spark):
    return (
        spark.read
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "silver.trip_updates")
        .option("user", DB_USER)
        .option("password", DB_PASS)
        .option("driver", "org.postgresql.Driver")
        .load()
    )

def build_features(df):
    df = (
        df
        .filter(col("route_id").isNotNull())
        .filter(col("update_ts").isNotNull())
        .filter(col("stop_schedule_relationship").isNotNull())
        .withColumn("hour_of_day", hour(col("update_ts")))
        .withColumn("day_of_week", dayofweek(col("update_ts")))
        .withColumn("label", when(
            col("stop_schedule_relationship") == "SKIPPED", 1.0
        ).otherwise(0.0))
    )

    # Balance dataset
    skipped = df.filter(col("label") == 1.0)
    not_skipped = df.filter(col("label") == 0.0).sample(
        fraction=skipped.count() / df.filter(col("label") == 0.0).count(),
        seed=42
    )
    return skipped.union(not_skipped)

def main():
    spark = (
        SparkSession.builder
        .appName("HSL Delay Prediction Model")
        .getOrCreate()
    )

    print("Reading silver data...")
    df = read_silver(spark)

    print("Building features...")
    df = build_features(df)

    # Encode route_id as numeric
    route_indexer = StringIndexer(
        inputCol="route_id",
        outputCol="route_id_indexed",
        handleInvalid="skip"
    )

    # Assemble features into a single vector
    assembler = VectorAssembler(
        inputCols=["route_id_indexed", "direction_id", "hour_of_day", "day_of_week"],
        outputCol="features",
        handleInvalid="skip"
    )

    # Random Forest classifier
    rf = RandomForestClassifier(
        featuresCol="features",
        labelCol="label",
        numTrees=50,
        maxDepth=5,
        maxBins=512,
        seed=42
    )

    # Build pipeline
    pipeline = Pipeline(stages=[route_indexer, assembler, rf])

    # Split train/test
    train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)
    print(f"Train size: {train_df.count()}, Test size: {test_df.count()}")

    # Train
    print("Training model...")
    model = pipeline.fit(train_df)

    # Evaluate
    predictions = model.transform(test_df)
    evaluator = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC"
    )
    auc = evaluator.evaluate(predictions)
    print(f"AUC: {auc:.4f}")

    # Save metrics to gold
    metrics_data = [(auc, train_df.count(), test_df.count())]
    metrics_df = spark.createDataFrame(
        metrics_data,
        ["auc_score", "train_size", "test_size"]
    )

    (
        metrics_df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "gold.ml_model_results")
        .option("user", DB_USER)
        .option("password", DB_PASS)
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print(f"Model training complete. AUC: {auc:.4f}")

    # Save the model
    model_path = "/app/models/delay_prediction_model"
    model.write().overwrite().save(model_path)
    print(f"Model saved to {model_path}")
    spark.stop()

if __name__ == "__main__":
    main()