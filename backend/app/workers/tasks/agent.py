from app.workers.celery_app import celery_app
from typing import Dict, Any
import asyncio
from app.agents.execution.engine import AgentExecutor
from app.agents.communication.bus import AgentBus

@celery_app.task(name="app.workers.tasks.agent.execute_task", bind=True, max_retries=3)
def execute_task(self, task_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker task that executes a specific agentic subtask using the AgentExecutor ReAct loop.
    """
    try:
        goal = task_definition.get("description", "No description provided")
        task_id = task_definition.get("id")
        print(f"Executing agent task: {goal}")
        
        async def _run_agent():
            # Use default workspace and gemini flash for fast execution
            executor = AgentExecutor(workspace_id="default_workspace", model_name="gemini/gemini-2.5-flash")
            bus = AgentBus()
            
            # Notify frontend task has started
            await bus.publish("system_events", {"event": "task_started", "task_id": task_id})
            
            result = await executor.execute_task(goal)
            
            # Publish result to bus
            await bus.publish(f"task_completed:{task_id}", {"result": result, "task_id": task_id})
            
            # Notify Orchestrator
            await bus.publish("TaskCompleted", task_id)
            
            # Notify Frontend
            await bus.publish("system_events", {"event": "task_completed", "task_id": task_id, "result": result})
            
            return result

        result = asyncio.run(_run_agent())
        
        return {"status": "success", "result": result}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2)
