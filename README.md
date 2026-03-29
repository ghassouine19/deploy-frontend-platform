# deploy-frontend-platform

Description
This repository is a scaffold for a platform that deploys frontend builds and collects deployment events for batch data engineering pipelines. The stack is oriented toward Data Engineer use-cases: incoming deployment events stored in S3, batch ETL via Airflow, and a backend to receive webhooks/uploads.

What's included (iteration 1)
- Backend: FastAPI service that receives GitHub webhooks and manual uploads, stores build artifacts to S3, and writes deployment metadata to a metadata DB.
- Ingestion: events are persisted as JSON files in an S3 bucket (partitioned by date) for batch processing.
- Orchestration: example Apache Airflow DAG that reads raw events from S3 and loads them into Postgres.
- CI: GitHub Actions workflow that builds a frontend (example), uploads artifacts to S3, and notifies the backend webhook.
- Dev infra: docker-compose for local development (backend, Postgres, Airflow).

Quickstart (local)
1. Copy files into a new repo `deploy-frontend-platform`.
2. Create `.env` from `.env.example` and fill values (AWS credentials, S3 bucket, DB URL, SECRET keys).
3. Build and run dev services:
   - docker-compose up --build
4. Open backend at http://localhost:8000
   - Health: GET /health
   - Webhook: POST /webhook (GitHub webhook or manual request)
   - Manual upload: POST /upload (multipart/form-data file=build.zip)
5. Start Airflow UI: http://localhost:8080 (default creds configured in docker-compose).

GitHub Actions (CI)
- Workflow builds frontend (if present), uploads to S3 using AWS credentials in secrets, and notifies the backend webhook (BACKEND_WEBHOOK_URL secret).

Recommended next steps
- Replace local SQLite (dev) with managed Postgres for production and/or configure Redshift/BigQuery as warehouse.
- Add data quality checks (Great Expectations), schema registry and partitioning strategy in S3.
- Add Terraform for infra (S3 buckets, IAM, RDS/Redshift, SNS topic for alerts).
- Extend Airflow DAGs to include transformations (PySpark / dbt) and orchestration for incremental loads.

Contributing
- Open issues, feature requests, or improvements via GitHub.
- Tests and CI are welcome additions.

License
MIT (see LICENSE file)
