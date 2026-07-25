from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime, timezone

from app.db.models.base import Base, UUIDMixin

class LoginAuditLog(Base, UUIDMixin):
    __tablename__ = "login_audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True) # Optional in case of unknown user
    email_attempted: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
