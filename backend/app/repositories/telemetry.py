from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.db.models.telemetry import AILog

class TelemetryRepository(BaseRepository[AILog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AILog, db)

    async def get_recent(self, skip: int = 0, limit: int = 50) -> List[AILog]:
        stmt = select(AILog).order_by(AILog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
