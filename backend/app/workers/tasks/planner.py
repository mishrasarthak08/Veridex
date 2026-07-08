from app.workers.celery_app import celery_app
from typing import Dict, Any

@celery_app.task(name="app.workers.tasks.planner.decompose_goal", bind=True, max_retries=3)
def decompose_goal(self, goal: str) -> Dict[str, Any]:
    """
    Worker task that takes a high-level goal and decomposes it into subtasks.
    """
    try:
        # Simulated LLM planner logic
        print(f"Decomposing goal: {goal}")
        tasks = [
            {"id": "t1", "action": "research", "details": "Search for documentation"},
            {"id": "t2", "action": "write", "details": "Draft a summary"}
        ]
        return {"status": "success", "subtasks": tasks}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
