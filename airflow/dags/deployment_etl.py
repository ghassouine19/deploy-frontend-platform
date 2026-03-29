from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import os
import json
import psycopg2

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def list_and_load(**context):
    s3 = boto3.client("s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )
    bucket = os.getenv("S3_BUCKET")
    prefix = "events/"
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    items = resp.get("Contents", [])
    # connect to Postgres
    pg = psycopg2.connect(
        host=os.getenv("DB_HOST","db"),
        dbname=os.getenv("DB_NAME","deployments"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","postgres"),
    )
    cur = pg.cursor()
    for obj in items:
        key = obj["Key"]
        if key.endswith(".json"):
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            data = json.loads(body)
            # Simple insert example: store repo name and raw payload
            repo = data.get("repository", {}).get("full_name", "unknown")
            cur.execute("INSERT INTO raw_events (repo, payload) VALUES (%s, %s) ON CONFLICT DO NOTHING", (repo, json.dumps(data)))
            pg.commit()
    cur.close()
    pg.close()

with DAG(
    dag_id="deployment_events_ingest",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
) as dag:
    task_ingest = PythonOperator(
        task_id="list_and_load",
        python_callable=list_and_load,
    )
    task_ingest