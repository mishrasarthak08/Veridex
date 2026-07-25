from fastapi import APIRouter
from app.observability.synthetic.generator import SyntheticDataGenerator
from app.observability.metrics.analytics import CostAnalytics

router = APIRouter()
generator = SyntheticDataGenerator()
analytics = CostAnalytics()

import json
import os

@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """
    Returns the AI execution trace for the Playground UI.
    """
    if os.path.exists("traces.jsonl"):
        with open("traces.jsonl", "r") as f:
            for line in f:
                trace = json.loads(line)
                if trace.get("trace_id") == trace_id:
                    return trace
    
    # Also check the global_recorder if it's currently active (for testing)
    from app.agents.orchestrator.manager import global_recorder
    if trace_id in global_recorder.active_traces:
        return global_recorder.active_traces[trace_id].model_dump()
        
    return {"error": "Trace not found"}

@router.post("/synthetic/generate")
async def generate_synthetic_data(count: int = 10):
    return generator.generate_tasks(count)

@router.get("/metrics/cost")
async def get_cost_analytics():
    return analytics.get_dashboard()
