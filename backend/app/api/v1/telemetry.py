from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.models.telemetry import AILog

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_telemetry_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=100)
) -> Any:
    """
    Retrieve recent AI telemetry logs.
    Currently only accessible to system admins.
    """
    if "system_admin" not in current_user.roles:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    stmt = select(AILog).order_by(AILog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "task_id": log.task_id,
            "model": log.model,
            "prompt_tokens": log.prompt_tokens,
            "completion_tokens": log.completion_tokens,
            "cost_usd": log.cost_usd,
            "latency_ms": log.latency_ms,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]
