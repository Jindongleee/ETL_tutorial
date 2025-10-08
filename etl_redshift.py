from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
file_path = 'redshift_users.csv'
# .env 쓰기
import os

# 운영 DB에서 extract
def extract_mysql(**context):
    mysql = MySqlHook(mysql_conn_id = 'mysql_default') #
    df = mysql.get_pandas_df('select * from users;') # db -> table로 변환
    df.to_csv(file_path, index=False) # 인덱스 제거
    context['ti'].xcom_push(key='file_path', value = file_path)

def transform_data(**context):
    file_path = context['ti'].xcom_pull(key='file_path', task_ids='extract')
    df = pd.read_csv(file_path) # 인덱스 제거 안하면 -> unnamed : 0생김
    df["name"] = df["name"].str.upper()
    df = df.fillna({"country":"UNKNOWN"})
    transformed_path = "users_clean.csv"
    df.to_csv(transformed_path)
    context['ti'].xcom_push(key="transformed_path", value = transformed_path)

# load s3
def load_to_s3(**context):
    transformed_path = context['ti'].xcom_pull(key="transformed_path", task_ids="transform")
    s3 = S3Hook(aws_conn_id="aws_default")
    bucket_name = 'etl-tutorial-of-eddy' # 실제 object storage bucket 이름
    key = 'users/users_clean.csv' # / 뒤 경로
    s3.load_file(filename=transformed_path, bucket_name=bucket_name, key=key, replace=True)
    context['ti'].xcom_push(key='s3_path', value=f's3://{bucket_name}/{key}') 


# s3 -> redshift
def copy_to_redshift(**context):
    load_dotenv()
    aws_iam = os.getenv("IAM")
    s3_path = context['ti'].xcom_pull(key = 's3_path', task_ids='load')
    redshift = PostgresHook(postgres_conn_id='redshift_default')
    conn = redshift.get_conn()
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    user_id INT,
                    name VARCHAR(50),
                    age INT,
                    country VARCHAR(50)
                );

                """)
    copy_sql = f"""
    COPY users
    FROM '{s3_path}'
    IAM_ROLE '{aws_iam}'
    CSV IGNOREHEADER 1;
    """
    cur.execute(copy_sql)
    conn.commit()
    cur.close()

with DAG(
    dag_id="etl_redshift",
    start_date=datetime(2025,10,6),
    schedule= "@daily",
    catchup=False
) as dag:
    extract = PythonOperator(task_id = "extract", python_callable=extract_mysql)
    transform = PythonOperator(task_id = "transform", python_callable=transform_data)
    load = PythonOperator(task_id="load", python_callable=load_to_s3)
    copy = PythonOperator(task_id="copy", python_callable=copy_to_redshift)
    extract >> transform >> load >> copy
