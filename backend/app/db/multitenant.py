from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class MultiTenantBase(DeclarativeBase):
    """
    All enterprise domain models should inherit from this base.
    It forces a tenant_id column on every row. Query interceptors
    must ensure that a user from Tenant A can never query rows 
    where tenant_id == Tenant B.
    """
    __abstract__ = True

    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
