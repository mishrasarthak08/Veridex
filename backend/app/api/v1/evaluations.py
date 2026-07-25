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

@router.get("/")
async def list_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List historical evaluation runs.
    """
    result = await db.execute(
        select(EvaluationRun).where(EvaluationRun.user_id == current_user.id).order_by(EvaluationRun.created_at.desc())
    )
    runs = result.scalars().all()
    
    # Map to frontend expectations
    mapped_runs = []
    for r in runs:
        mapped_runs.append({
            "id": str(r.id),
            "dataset_name": r.dataset_name,
            "query": r.metrics.get("query", "Default query trace"),
            "scores": {
                "relevance": r.metrics.get("accuracy", r.average_score / 10.0 if r.average_score else 0.0),
                "hallucination": r.metrics.get("hallucination_rate", 0.0)
            },
            "overall_passed": r.average_score is not None and r.average_score >= 7.0,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
        
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
    import os
    import json
    from app.ai.evaluation.judge import LLMJudge
    
    # Simple logic: evaluate the last trace from traces.jsonl
    last_trace = None
    if os.path.exists("traces.jsonl"):
        with open("traces.jsonl", "r") as f:
            lines = f.readlines()
            if lines:
                last_trace = json.loads(lines[-1])
                
    if not last_trace:
        return {"status": "error", "message": "No traces available to evaluate"}
        
    judge = LLMJudge()
    
    # Create the db record immediately as 'running'
    eval_run = EvaluationRun(
        id=str(uuid.uuid4()),
        dataset_name="golden_dataset_v1",
        metrics={"accuracy": 0.0, "hallucination_rate": 0.0},
        average_score=0.0,
        user_id=current_user.id
    )
    db.add(eval_run)
    await db.commit()
    await db.refresh(eval_run)
    
    # We would normally do this in a background task
    # For demonstration, we'll await it directly to get immediate feedback
    eval_res = await judge.evaluate_execution(
        exec_id=last_trace.get("trace_id", ""),
        goal=last_trace.get("goal", ""),
        result="Mock result from trace." # in real implementation we fetch final result
    )
    
    eval_run.average_score = eval_res.score
    eval_run.metrics = {"feedback": eval_res.feedback, "accuracy": eval_res.score / 10.0}
    await db.commit()
    await db.refresh(eval_run)

    mapped_run = {
        "id": str(eval_run.id),
        "dataset_name": eval_run.dataset_name,
        "query": last_trace.get("goal", "Default query trace") if last_trace else "Default query trace",
        "scores": {
            "relevance": eval_run.metrics.get("accuracy", eval_run.average_score / 10.0 if eval_run.average_score else 0.0),
            "hallucination": eval_run.metrics.get("hallucination_rate", 0.0)
        },
        "overall_passed": eval_run.average_score is not None and eval_run.average_score >= 7.0,
        "created_at": eval_run.created_at.isoformat() if eval_run.created_at else None
    }

    return {"status": "completed", "run_id": eval_run.id, "data": mapped_run}
