from app.workers.celery_app import celery_app
from typing import Dict, Any
import asyncio
from app.agents.planner.engine import PlanningEngine
from app.agents.scheduler.queue import TaskScheduler

@celery_app.task(name="app.workers.tasks.planner.decompose_goal", bind=True, max_retries=3)
def decompose_goal(self, goal: str) -> Dict[str, Any]:
    """
    Worker task that takes a high-level goal and decomposes it into subtasks.
    """
    try:
        print(f"Decomposing goal: {goal}")
        
        async def _decompose_and_enqueue():
            planner = PlanningEngine()
            scheduler = TaskScheduler()
            
            tasks = await planner.decompose(goal)
            for task in tasks:
                await scheduler.enqueue(task)
            
            return [t.to_dict() for t in tasks]

        tasks_dict = asyncio.run(_decompose_and_enqueue())
        
        return {"status": "success", "subtasks": tasks_dict}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
