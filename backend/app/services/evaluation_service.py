from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.evaluation import EvaluationRepository
from app.db.models.evaluation import EvaluationRun
import uuid
import os
import json

class EvaluationService:
    def __init__(self, db: AsyncSession):
        self.repo = EvaluationRepository(db)

    async def list_evaluations(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        runs = await self.repo.get_by_user_desc(user_id)
        
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
            
        return mapped_runs

    async def trigger_evaluation(self, user_id: uuid.UUID) -> Tuple[bool, str, Dict[str, Any]]:
        # Simple logic: evaluate the last trace from traces.jsonl
        last_trace = None
        if os.path.exists("traces.jsonl"):
            with open("traces.jsonl", "r") as f:
                lines = f.readlines()
                if lines:
                    last_trace = json.loads(lines[-1])
                    
        if not last_trace:
            return False, "No traces available to evaluate", {}
            
        from app.ai.evaluation.judge import LLMJudge
        judge = LLMJudge()
        
        eval_run = await self.repo.create({
            "id": str(uuid.uuid4()),
            "dataset_name": "golden_dataset_v1",
            "metrics": {"accuracy": 0.0, "hallucination_rate": 0.0},
            "average_score": 0.0,
            "user_id": user_id
        })
        
        eval_res = await judge.evaluate_execution(
            exec_id=last_trace.get("trace_id", ""),
            goal=last_trace.get("goal", ""),
            result="Mock result from trace." # in real implementation we fetch final result
        )
        
        eval_run = await self.repo.update(eval_run, {
            "average_score": eval_res.score,
            "metrics": {"feedback": eval_res.feedback, "accuracy": eval_res.score / 10.0}
        })
        
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

        return True, str(eval_run.id), mapped_run
