from sqlalchemy import String, ForeignKey, Table, Column, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import uuid

from app.db.models.base import Base, UUIDMixin, TimestampMixin

# Association table for Many-to-Many relationship between Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Uuid, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Uuid, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Many-to-Many relationship between Users and Roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Uuid, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )

    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles"
    )
