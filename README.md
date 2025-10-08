uv 기반 가상환경 사용

# ETL_Project
Extract(운영DB, 데이터포털, SNS) -> Transform(Pandas, Spark ML, Spark, Hadoop) -> Load(S3, AWS Redshift, GCP BigQuery), HBase) 사용예정

--

### airflow를 위해 .env 사용

- cd [project 위치]
   - export $(cat .env | xargs) // airflow.cfg 파일 lite 버전 덮어씌우기 위함
   - airflow db migrate
   - airflow api-server --port 
   - airflow triggler
   - airflow dag-processor 

위에 안쓰고 airflow standalone 일단 사용 예정

## Flow

-- Airflow --
Mysql dump -> transform (pandas) -> load to s3 -> copy s3 to redshift

Airflow Connection 설정
1. Mysql_default (docker create -> mysql), (mac os, ubuntu -> default IPv6 따라서
   - host: 127.0.0.1, port:3306, db:ariflow_db)
---
2. AWS_S3_default, IAM (AmaazonS3FullAccess) 생성
   - AWS Access Key ID = IAM Access Key
   - AWS Secret Access Key = IAM Secret Key
   - 추가 필드 JSON: {
        "region_name": "ap-northeast-2"
     }
---
3. redshift_dafault, IAM role 생성 redshift -> AmazonS3ReadOnlyAccess -> 네임스페이스 보안 및 암호화 IAM 역할 관리 -> role 연결
   - host: redshift 작업그룹 엔드포인트
   - User: 네임스페이스 user
   - 비밀번호: 네임스페이스 -> 작업 토글 관리자 보안
   - port: 5439
   - db: 네임스페이스 데이터베이스 이름
   - 추가 필드 JSON: {
        "sslmode": "require" 
     }

결과 Redshift -> query editor v2

<img width="1000" height="650" alt="image" src="https://github.com/user-attachments/assets/19ab978c-0af0-4c11-8087-17b0d02cf13d" />
