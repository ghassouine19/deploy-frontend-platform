from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./metadata.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Deployment(Base):
    __tablename__ = "deployments"
    id = Column(String, primary_key=True, index=True)
    repo = Column(String, index=True)
    s3_key = Column(String)
    is_event = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_deployment(deploy_id: str, repo: str, s3_key: str, event: bool = False):
    db = SessionLocal()
    d = Deployment(id=deploy_id, repo=repo, s3_key=s3_key, is_event=event)
    db.add(d)
    db.commit()
    db.close()