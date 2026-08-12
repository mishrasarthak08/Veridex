from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.db.models.audit import LoginAuditLog

class AuditRepository(BaseRepository[LoginAuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(LoginAuditLog, db)
