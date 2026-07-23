from app.agents.registry.tools import tool

@tool
def calculate_math(expression: str) -> str:
    """
    Evaluates a simple mathematical expression.
    Useful for basic arithmetic.
    """
    try:
        # Extremely dangerous in production, but okay for a trusted sandbox
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def search_web(query: str) -> str:
    """
    Searches the web for current information.
    Use this when you need up to date facts.
    """
    # Placeholder for a real web search tool like Tavily or Serper
    return f"Simulated search results for: {query}"

import uuid
from app.agents.approval.layer import global_approval_layer
from app.agents.communication.bus import AgentBus

@tool
async def execute_production_query(query: str) -> str:
    """
    Executes a high-risk production query or action.
    Requires human approval.
    """
    bus = AgentBus()
    task_id = str(uuid.uuid4())
    context = f"Request to execute production query: {query}"
    
    await bus.publish("system_events", {
        "event": "approval_requested",
        "task_id": task_id,
        "context": context
    })
    
    decision = await global_approval_layer.request_approval(task_id, context)
    
    if decision == "approve":
        return f"Production query executed successfully: {query}"
    elif decision == "revise":
        return f"Production query needs revision."
    else:
        return f"Production query rejected."

@tool
async def delegate_task(goal: str, target_agent: str) -> str:
    """
    Delegates a sub-goal or task to another specialized agent.
    """
    from app.agents.planner.engine import TaskNode
    from app.agents.scheduler.queue import TaskScheduler

    scheduler = TaskScheduler()
    task = TaskNode(description=goal, agent_role=target_agent)
    await scheduler.enqueue(task)
    return f"Task '{goal}' delegated to {target_agent} with ID {task.id}"
