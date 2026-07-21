import pytest
import asyncio
from unittest.mock import patch

from app.workers.tasks.planner import decompose_goal
from app.workers.tasks.agent import execute_task
from app.agents.communication.bus import AgentBus

@pytest.mark.asyncio
async def test_orchestrator_full_cycle():
    """
    Test the full decomposition -> scheduling -> execution cycle.
    We mock the LLM network call to save credits, but exercise all Celery and Redis plumbing.
    """
    bus = AgentBus()
    
    with patch("app.workers.tasks.agent.execute_task.apply_async") as mock_apply:
        
        with patch("app.ai.router.router.generate") as mock_llm:
            # Provide a canned LLM response
            mock_llm.return_value = {
                "choices": [{"message": {"content": "MOCKED_SUCCESS"}}]
            }
            
            # 1. Trigger the planner in a thread since it uses asyncio.run() internally
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, decompose_goal, "Do some research")
            
            assert result["status"] == "success"
            assert len(result["subtasks"]) == 1
            
            task_node = result["subtasks"][0]
            task_id = task_node["id"]
            
            # 2. Subscribe and then execute
            async def run_worker():
                args, kwargs = mock_apply.call_args
                # args might be empty if kwargs were used (e.g., args=[task_dict], queue=...)
                task_dict = kwargs.get("args", args[0] if args else None)[0]
                # Run the task logic (which publishes to the bus) in a thread as well
                await loop.run_in_executor(None, execute_task, task_dict)
            
            # Start subscribing
            listen_task = asyncio.create_task(bus.wait_for(f"task_completed:{task_id}"))
            
            # Allow subscriber to connect to Redis
            await asyncio.sleep(0.1)
            
            # Trigger the fake worker execution
            await run_worker()
            
            # Await the published result
            event_data = await listen_task
            
            assert event_data["task_id"] == task_id
            assert event_data["result"] == "MOCKED_SUCCESS"
