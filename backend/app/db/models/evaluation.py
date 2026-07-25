from sqlalchemy import Column, String, Uuid, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.models.base import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String, primary_key=True, index=True)
    dataset_name = Column(String, nullable=False)
    metrics = Column(JSON, default=dict)
    average_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
