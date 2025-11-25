from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
sys.path.append('/opt/airflow/src')
from extract import run_all_feed


default_args = {
    'owner': 'Juan Esteban',
    'start_date': days_ago(1),
    'email': 'juanillo@hello.com',
    'email_on_failure': True,
    'email_on_retry': True,
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
    output_dir = "../data/raw"
    run_all_feed(output_dir)



# Define tasks

#Task 1: Extract the Data
extract_data = PythonOperator(
    task_id='extract_data',
    python_callable=run_extractor,
    dag=dag
)

extract_data