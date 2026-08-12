from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.db.models.connector import ConnectorConfig
import uuid

class ConnectorRepository(BaseRepository[ConnectorConfig]):
    def __init__(self, db: AsyncSession):
        super().__init__(ConnectorConfig, db)

    async def get_by_user(self, user_id: uuid.UUID) -> List[ConnectorConfig]:
        stmt = select(ConnectorConfig).where(ConnectorConfig.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, connector_id: str, user_id: uuid.UUID) -> ConnectorConfig | None:
        stmt = select(ConnectorConfig).where(
            ConnectorConfig.id == connector_id,
            ConnectorConfig.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
