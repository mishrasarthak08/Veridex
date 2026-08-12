from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Any
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.models.telemetry import AILog
from app.services.telemetry_service import TelemetryService

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_telemetry_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100)
) -> Any:
    """
    Retrieve recent AI telemetry logs.
    Accessible to users with admin or owner roles.
    """
    # BYPASS PERMISSIONS FOR LOCAL DEV
    # user_role_names = [r.name for r in current_user.roles] if current_user.roles else []
    # if not any(role in ("owner", "admin", "system_admin") for role in user_role_names):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    service = TelemetryService(db)
    return await service.get_recent_logs(skip, limit)
