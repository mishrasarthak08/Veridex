from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat import ChatRepository
import uuid

class ChatService:
    def __init__(self, db: AsyncSession):
        self.repo = ChatRepository(db)

    async def get_user_threads(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        threads = await self.repo.get_threads_by_user(user_id)
        return [
            {
                "thread_id": row.thread_id,
                "last_updated": row.last_updated.isoformat() if row.last_updated else None
            }
            for row in threads
        ]

    async def get_thread_history(self, thread_id: str, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        messages = await self.repo.get_history_by_thread(thread_id, user_id)
        return [
            {
                "id": msg.id,
                "thread_id": msg.thread_id,
                "role": msg.role,
                "content": msg.content,
                "traces": msg.traces,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            for msg in messages
        ]

    async def add_message(self, thread_id: str, role: str, content: str, traces: list, user_id: uuid.UUID) -> Dict[str, Any]:
        obj_in = {
            "id": str(uuid.uuid4()),
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "traces": traces,
            "user_id": user_id
        }
        new_message = await self.repo.create(obj_in)
        return {
            "id": new_message.id,
            "thread_id": new_message.thread_id,
            "role": new_message.role,
            "content": new_message.content,
            "traces": new_message.traces,
            "created_at": new_message.created_at.isoformat() if new_message.created_at else None
        }
