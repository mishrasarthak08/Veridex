from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.repositories.base import BaseRepository
from app.db.models.chat import ChatHistory
import uuid

class ChatRepository(BaseRepository[ChatHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatHistory, db)

    async def get_threads_by_user(self, user_id: uuid.UUID) -> List[Any]:
        stmt = select(
            ChatHistory.thread_id, 
            func.max(ChatHistory.created_at).label('last_updated')
        ).where(
            ChatHistory.user_id == user_id
        ).group_by(
            ChatHistory.thread_id
        ).order_by(
            func.max(ChatHistory.created_at).desc()
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def get_history_by_thread(self, thread_id: str, user_id: uuid.UUID) -> List[ChatHistory]:
        stmt = select(ChatHistory).where(
            ChatHistory.thread_id == thread_id,
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
