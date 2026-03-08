from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
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
    schedule_interval=None,
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

run_spark_vehicle_positions = BashOperator(
    task_id="run_spark_vehicle_positions",
    bash_command="""
    spark-submit \
      --jars /app/jars/postgresql-42.7.3.jar \
      /app/spark_jobs/02_vehicle_positions_silver.py
    """,
    dag=dag,
)

extract_data >> run_spark_vehicle_positions