from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def print_hello():
    print("Hello, Airflow!")

with DAG(
    dag_id='my_first_dag',
    start_date=datetime(2025, 8, 10),
    schedule='@daily',       # schedule_interval → schedule 로 변경
    catchup=False
) as dag:
    task1 = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello
    )
