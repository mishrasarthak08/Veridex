from app.workers.celery_app import celery_app
from typing import Dict, Any
import asyncio
from app.ai.runtime.agent import AgentRuntime
from app.agents.communication.bus import AgentBus

@celery_app.task(name="app.workers.tasks.agent.execute_task", bind=True, max_retries=3)
def execute_task(self, task_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker task that executes a specific agentic subtask.
    """
    try:
        goal = task_definition.get("description", "No description provided")
        task_id = task_definition.get("id")
        print(f"Executing agent task: {goal}")
        
        async def _run_agent():
            runtime = AgentRuntime()
            bus = AgentBus()
            
            result = await runtime.execute(goal)
            
            # Publish result to bus
            await bus.publish(f"task_completed:{task_id}", {"result": result, "task_id": task_id})
            return result

        result = asyncio.run(_run_agent())
        
        return {"status": "success", "result": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2)
