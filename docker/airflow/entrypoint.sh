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

# Start Airflow webserver or scheduler depending on the container
exec airflow "$@"
