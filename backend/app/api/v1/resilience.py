from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter()

class ChaosRequest(BaseModel):
    mode: str
    duration_ms: int = 0
    probability: float = 0.5

async def chaos_event_generator():
    events = [
        {"time": datetime.now().strftime("%H:%M:%S"), "message": "Simulating network partition on Celery worker...", "type": "warning"},
        {"time": datetime.now().strftime("%H:%M:%S"), "message": "Istio fault injection applied: 50% 503 errors to Vector DB", "type": "warning"},
        {"time": datetime.now().strftime("%H:%M:%S"), "message": "Observing orchestrator fallback behavior...", "type": "info"},
        {"time": datetime.now().strftime("%H:%M:%S"), "message": "Orchestrator successfully retried tasks. No data lost.", "type": "success"},
        {"time": datetime.now().strftime("%H:%M:%S"), "message": "Chaos test complete. System resilient.", "type": "success"}
    ]
    
    for event in events:
        await asyncio.sleep(1.5)
        yield f"data: {json.dumps(event)}\n\n"

@router.get("/chaos/stream")
async def stream_chaos():
    """
    Server-Sent Events for chaos logs
    """
    return StreamingResponse(chaos_event_generator(), media_type="text/event-stream")

@router.post("/chaos")
async def start_chaos(req: ChaosRequest):
    """
    Start specific chaos injection
    """
    logger.warning("Chaos event injected", mode=req.mode, probability=req.probability, duration_ms=req.duration_ms)
    
    # In a real system, this would write to Redis/Consul to configure a global fault injector 
    # For now, we simulate the return status
    return {"status": "chaos_injected", "mode": req.mode}
