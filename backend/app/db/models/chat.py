from sqlalchemy import Column, String, Uuid, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.models.base import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, index=True)
    thread_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    traces = Column(JSON, default=list)  # Store execution timeline logs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
