from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.db.models.base import Base
import uuid

class AILog(Base):
    __tablename__ = "ai_logs"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, index=True, nullable=True) # Optional link to a specific Celery/Agent task
    model = Column(String, index=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)
    
    # Store arbitrary metadata (e.g., prompt name, version, evaluation scores)
    metadata_ = Column("metadata", JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
