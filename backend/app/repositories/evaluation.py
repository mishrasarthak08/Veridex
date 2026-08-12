from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.db.models.evaluation import EvaluationRun
import uuid

class EvaluationRepository(BaseRepository[EvaluationRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(EvaluationRun, db)

    async def get_by_user_desc(self, user_id: uuid.UUID) -> List[EvaluationRun]:
        stmt = select(EvaluationRun).where(
            EvaluationRun.user_id == user_id
        ).order_by(EvaluationRun.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
