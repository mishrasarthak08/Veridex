from app.workers.celery_app import celery_app
from typing import Dict, Any

@celery_app.task(name="app.workers.tasks.agent.execute_task", bind=True, max_retries=3)
def execute_task(self, task_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker task that executes a specific agentic subtask.
    """
    try:
        action = task_definition.get("action")
        print(f"Executing agent task: {action}")
        
        # Simulated agent execution
        result = f"Completed action: {action}"
        return {"status": "success", "result": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2)
