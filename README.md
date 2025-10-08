uv 기반 가상환경 사용

# ETL_Project
데이터 생성 및 수집(Apache Kafka), 저장(HDFS, AWS S3), 변환(Apache Airflow, Spark), 서빙(Apache Superset)

--

### airflow를 위해 .env 사용

- cd [project 위치]
- export $(cat .env | xargs)
- airflow db migrate
- airflow api-server --port 8080

- 어떠 db가 붙었는지 확인을 위해서 -> airflow info | grep -i database