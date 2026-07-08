from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.db.models.base import Base, UUIDMixin, TimestampMixin

class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(255), nullable=False) # e.g., 'project', 'workspace'
    action: Mapped[str] = mapped_column(String(255), nullable=False)   # e.g., 'create', 'read', 'update', 'delete'
    
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )
