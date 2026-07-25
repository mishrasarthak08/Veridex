from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Any
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.models.chat import ChatHistory
from pydantic import BaseModel
from app.core.rate_limit import limiter

router = APIRouter()

class ChatMessageCreate(BaseModel):
    thread_id: str
    role: str
    content: str
    traces: list = []

@router.get("/threads")
async def get_chat_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve all unique chat threads for the current user, ordered by most recently updated.
    """
    # We group by thread_id and get the max created_at for sorting
    stmt = select(
        ChatHistory.thread_id, 
        func.max(ChatHistory.created_at).label('last_updated')
    ).where(
        ChatHistory.user_id == current_user.id
    ).group_by(
        ChatHistory.thread_id
    ).order_by(
        func.max(ChatHistory.created_at).desc()
    )
    
    result = await db.execute(stmt)
    threads = result.all()
    
    return [
        {
            "thread_id": row.thread_id,
            "last_updated": row.last_updated.isoformat() if row.last_updated else None
        }
        for row in threads
    ]


@router.get("/history/{thread_id}")
async def get_chat_history(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve chat history for a specific thread_id.
    """
    stmt = select(ChatHistory).where(
        ChatHistory.thread_id == thread_id,
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.asc())
    
    result = await db.execute(stmt)
    messages = result.scalars().all()
    
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

@router.post("/message")
@limiter.limit("20/minute")
async def add_chat_message(
    request: Request,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Save a new chat message to history.
    """
    new_message = ChatHistory(
        id=str(uuid.uuid4()),
        thread_id=message_in.thread_id,
        role=message_in.role,
        content=message_in.content,
        traces=message_in.traces,
        user_id=current_user.id
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    
    return {
        "id": new_message.id,
        "thread_id": new_message.thread_id,
        "role": new_message.role,
        "content": new_message.content,
        "traces": new_message.traces,
        "created_at": new_message.created_at.isoformat() if new_message.created_at else None
    }
