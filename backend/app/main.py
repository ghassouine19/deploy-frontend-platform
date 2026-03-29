from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from .s3_client import S3Client
from .models import init_db, save_deployment

app = FastAPI(title="Deployment Ingest API")

S3_BUCKET = os.getenv("S3_BUCKET")
s3 = S3Client()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_build(file: UploadFile = File(...), repo: str = ""):
    if not S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    content = await file.read()
    deploy_id = str(uuid.uuid4())
    key = f"deployments/{repo}/{deploy_id}/build.zip"
    s3.upload_bytes(S3_BUCKET, key, content, content_type=file.content_type)
    # persist metadata
    save_deployment(deploy_id, repo, key)
    return JSONResponse({"deploy_id": deploy_id, "s3_key": key})

@app.post("/webhook")
async def github_webhook(x_github_event: str | None = Header(None), payload: dict | None = None):
    # Minimal webhook parser: expects JSON with repository.full_name and a build artifact URL (or trigger)
    if payload is None:
        raise HTTPException(status_code=400, detail="Missing payload")
    repo = payload.get("repository", {}).get("full_name", "unknown")
    deploy_id = str(uuid.uuid4())
    # store raw webhook event into S3 for batch processing
    key = f"events/{repo}/raw/{deploy_id}.json"
    s3.upload_json(S3_BUCKET, key, payload)
    save_deployment(deploy_id, repo, key, event=True)
    return {"status": "accepted", "deploy_id": deploy_id}