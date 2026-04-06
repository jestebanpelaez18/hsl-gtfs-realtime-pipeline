from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys

sys.path.append('/opt/airflow/src')
from extract import run_all_feed

default_args = {
    "owner": "Juan Esteban",
    "start_date": days_ago(1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "gtfs_realtime_dag",
    default_args=default_args,
    schedule_interval="*/30 * * * *",
    catchup=False,
    is_paused_upon_creation=False,
)

def run_extractor():
    output_dir = "/opt/airflow/data/raw"
    run_all_feed(output_dir)

extract_data = PythonOperator(
    task_id="extract_data",
    python_callable=run_extractor,
    dag=dag,
)

run_spark_vehicle_positions = SparkSubmitOperator(
    task_id="spark_vehicle_positions",
    application="/opt/airflow/spark_jobs/02_vehicle_positions_silver.py",
    conn_id="spark_default",
    jars="/opt/airflow/jars/postgresql-42.7.3.jar",
    dag=dag,
)

run_spark_trip_updates = SparkSubmitOperator(
    task_id="spark_trip_updates",
    application="/opt/airflow/spark_jobs/03_trip_updates_silver.py",
    conn_id="spark_default",
    jars="/opt/airflow/jars/postgresql-42.7.3.jar",
    dag=dag,
)


run_dbt = BashOperator(
    task_id="dbt_run",
    bash_command="docker exec hsl_dbt dbt run --profiles-dir /app/dbt",
    dag=dag,
)

run_spark_predict = BashOperator(
    task_id="spark_predict_skipped_stops",
    bash_command="""
    docker exec hsl_spark spark-submit \
      --jars /app/jars/postgresql-42.7.3.jar \
      /app/spark_jobs/05_predict_skipped_stops.py
    """,
    dag=dag,
)

extract_data >> run_spark_vehicle_positions >> run_spark_trip_updates >> run_dbt >> run_spark_predict