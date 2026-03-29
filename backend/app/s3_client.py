# Local storage replacement for S3Client — writes artifacts and events to filesystem
import os
import json
from pathlib import Path

class S3Client:
    def __init__(self):
        # LOCAL_STORAGE_PATH points to a directory mounted or inside the container
        # e.g. ./storage
        self.base_path = Path(os.getenv("LOCAL_STORAGE_PATH", "./storage"))
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload_bytes(self, bucket, key, data: bytes, content_type="application/zip"):
        # bucket and key are kept for compatibility with existing code.
        # key is used to create nested directories under base_path.
        target = self.base_path / key
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)

    def upload_json(self, bucket, key, obj):
        target = self.base_path / key
        target.parent.mkdir(parents=True, exist_ok=True)
        body = json.dumps(obj, default=str, indent=2).encode("utf-8")
        with open(target, "wb") as f:
            f.write(body)