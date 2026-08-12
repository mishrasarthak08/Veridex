from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.models.evaluation import EvaluationRun

router = APIRouter()

class EvaluationRunCreate(BaseModel):
    dataset_name: str
    metrics: Dict[str, Any]
    average_score: float

from app.services.evaluation_service import EvaluationService

@router.get("/")
async def list_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List historical evaluation runs.
    """
    service = EvaluationService(db)
    mapped_runs = await service.list_evaluations(current_user.id)
    return {"data": mapped_runs}

@router.post("/run")
async def trigger_evaluation(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a new evaluation run.
    """
    service = EvaluationService(db)
    success, run_id_or_msg, mapped_run = await service.trigger_evaluation(current_user.id)
    
    if not success:
        return {"status": "error", "message": run_id_or_msg}

    return {"status": "completed", "run_id": run_id_or_msg, "data": mapped_run}
