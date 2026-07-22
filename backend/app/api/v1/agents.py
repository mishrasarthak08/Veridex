from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from app.agents.orchestrator.manager import Orchestrator
from app.agents.approval.layer import global_approval_layer
from sse_starlette.sse import EventSourceResponse
from app.agents.communication.bus import AgentBus
import json
router = APIRouter()

# Global instances for now
orchestrator = Orchestrator()
approval_layer = global_approval_layer
agent_bus = AgentBus()

class GoalRequest(BaseModel):
    goal: str

class ApprovalDecision(BaseModel):
    task_id: str
    decision: str  # 'approve', 'reject', 'revise'

@router.post("/goal")
async def submit_goal(request: GoalRequest, background_tasks: BackgroundTasks):
    """
    Submits a complex goal to the Orchestrator, which breaks it into a DAG
    and schedules it across multiple specialized agents.
    """
    background_tasks.add_task(orchestrator.execute_goal, request.goal)
    return {"status": "Goal submitted for multi-agent orchestration", "goal": request.goal}

@router.post("/approve")
async def submit_approval(decision: ApprovalDecision):
    """
    Endpoint for a human to approve or reject a pending sensitive action.
    """
    if decision.task_id not in approval_layer.pending_approvals:
        raise HTTPException(status_code=404, detail="Task not waiting for approval")
        
    approval_layer.submit_decision(decision.task_id, decision.decision)
    return {"status": "Decision recorded", "task_id": decision.task_id}

@router.get("/timeline")
async def execution_timeline():
    """
    SSE Endpoint for streaming the Execution Timeline UI in real-time.
    Listens to the 'system_events' channel on the AgentBus.
    """
    async def event_generator():
        yield {"event": "timeline_update", "data": json.dumps({"message": "Connecting to Agent Bus..."})}
        
        async for event_data in agent_bus.listen("system_events"):
            yield {"event": "timeline_update", "data": json.dumps(event_data)}
        
    return EventSourceResponse(event_generator())
