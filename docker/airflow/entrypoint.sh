#!/bin/bash
# Entrypoint for Airflow containers

# Initialize the Airflow DB
airflow db init

# Create user if not already created
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Add Spark connection if it doesn't exist
airflow connections delete spark_default 2>/dev/null || true
airflow connections add spark_default \
    --conn-type spark \
    --conn-host "local[*]" \
    2>/dev/null || true

# Start Airflow webserver or scheduler depending on the container
exec airflow "$@"