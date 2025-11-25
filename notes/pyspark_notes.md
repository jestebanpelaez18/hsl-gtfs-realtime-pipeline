# PySpark Notes 🧠

## 🧩 Spark Basics

- `SparkSession`: entry point to Spark
- `DataFrame`: distributed table-like structure
- Spark uses **lazy evaluation** — transformations are not run until an **action** is triggered (e.g. `.show()` or `.count()`)

## 🔥 My Common Commands

```python
from pyspark.sql import SparkSession

# Start Spark
spark = SparkSession.builder.appName("GTFS").getOrCreate()

# Read JSON
df = spark.read.json("data/raw/vehicle_positions_*.json")

# Inspect
df.printSchema()
df.show()

```

## Transformations I’ll Use

```python
select("trip.trip_id", "vehicle.position.latitude")

withColumn("lat", df["vehicle"]["position"]["latitude"])

filter(df["vehicle"]["position"]["latitude"].isNotNull())
```