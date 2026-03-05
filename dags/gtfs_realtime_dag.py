from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
sys.path.append('/opt/airflow/src')
from extract import run_all_feed
import os
from databricks_utils import  upload_to_workspace, run_databricks_job


default_args = {
    'owner': 'Juan Esteban',
    'start_date': days_ago(1),
    'email': 'juanillo@hello.com',
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('gtfs_realtime_dag',
          description='Realtime DAG for gtfs',
          default_args=default_args,
          schedule_interval=timedelta(days=1),
          )


# Extractor function: This gets the data from HSL API and format it to JSON
def run_extractor():
    output_dir = "/opt/airflow/data/raw"
    run_all_feed(output_dir)

def upload_latest_vehicle_positions():
    raw_data_dir = "/opt/airflow/data/raw/vehicle_positions"

    # Find the latest vehicle positions file
    vehicle_files = [f for f in os.listdir(raw_data_dir) if f.startswith("vehicle_positions_") and f.endswith(".jsonl")]
    if not vehicle_files:
        raise FileNotFoundError("No vehicle position files found.")

    latest_file = max(vehicle_files, key=lambda x: os.path.getctime(os.path.join(raw_data_dir, x)))
    latest_file_path = os.path.join(raw_data_dir, latest_file)
    
    # Upload the latest vehicle positions file to Databricks
    print(f"Uploading latest vehicle positions to Databricks: {latest_file_path}")
    workspace_path = upload_to_workspace(latest_file_path)
    print("Uploaded to workspace:", workspace_path)

    return workspace_path


# Define tasks

#Task 1: Extract the Data
extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=run_extractor,
    dag=dag
)

#Task 2: Upload Data to DataBricks
upload_data_to_databricks = PythonOperator(
    task_id='upload_data_to_databricks',
    python_callable=upload_latest_vehicle_positions,
    dag=dag
)   

# Task 3: Run the notebook on Databricks
run_notebook = PythonOperator(
    task_id='run_notebook_on_databricks',
    python_callable=run_databricks_job,
    dag=dag
)   

extract_data >> upload_data_to_databricks >> run_notebook