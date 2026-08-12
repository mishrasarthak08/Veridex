from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from app.agents.orchestrator.manager import Orchestrator
from app.agents.approval.layer import global_approval_layer
from sse_starlette.sse import EventSourceResponse
from app.agents.communication.bus import AgentBus
from app.core.rate_limit import limiter
from app.api.deps import get_current_user
from app.governance.audit import ImmutableAuditLog
from enum import Enum
import json

router = APIRouter()

orchestrator = Orchestrator()
approval_layer = global_approval_layer
agent_bus = AgentBus()
audit_log = ImmutableAuditLog()

class AgentState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETE = "complete"
    FAILED = "failed"

class GoalRequest(BaseModel):
    goal: str

class ApprovalDecision(BaseModel):
    task_id: str
    decision: str  # 'approve', 'reject', 'revise'

async def run_agent_lifecycle(goal: str, tenant_id: str, user_id: str):
    async def log_transition(state: AgentState, details: dict = None):
        await audit_log.log_action(
            tenant_id=tenant_id,
            actor=f"System-Agent",
            action="AGENT_STATE_TRANSITION",
            resource=f"Goal",
            details={"state": state.value, "goal": goal, **(details or {})},
            decision="ALLOW"
        )
        await agent_bus.publish("system_events", {"event": "agent_state_update", "state": state.value})

    await log_transition(AgentState.PLANNING)
    try:
        await log_transition(AgentState.EXECUTING)
        await orchestrator.execute_goal(goal)
        await log_transition(AgentState.COMPLETE)
    except Exception as e:
        await log_transition(AgentState.FAILED, {"error": str(e)})

@router.get("/")
async def list_agents():
    return {"status": "ok", "agents": ["orchestrator", "approval", "communication"]}

@router.post("/goal")
@limiter.limit("5/minute")
async def submit_goal(request: Request, goal_request: GoalRequest, background_tasks: BackgroundTasks, current_user = Depends(get_current_user)):
    """
    Submits a complex goal to the Orchestrator. 
    Tracks lifecycle states and writes to the Immutable Audit Log.
    """
    background_tasks.add_task(run_agent_lifecycle, goal_request.goal, str(current_user.tenant_id), str(current_user.id))
    return {"status": "Goal submitted for multi-agent orchestration", "goal": goal_request.goal}

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
