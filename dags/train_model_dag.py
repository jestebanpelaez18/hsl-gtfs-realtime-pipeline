from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    "owner": "Juan Esteban",
    "start_date": days_ago(1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}   

dag = DAG(
    "train_model_dag",
    default_args=default_args,
    schedule_interval="0 3 * * *",
    catchup=False,
    is_paused_upon_creation=False,
    description="DAG to train the delay prediction model every week",
)   

train_model = BashOperator(
    task_id="train_delay_model",
        bash_command="""
    docker exec hsl_spark spark-submit \
      --jars /app/jars/postgresql-42.7.3.jar \
      /app/spark_jobs/04_train_delay_model.py
    """,
    dag=dag,
)   