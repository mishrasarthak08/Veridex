from fastapi import APIRouter
from app.observability.synthetic.generator import SyntheticDataGenerator
from app.observability.metrics.analytics import CostAnalytics

router = APIRouter()
generator = SyntheticDataGenerator()
analytics = CostAnalytics()

@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """
    Returns the AI execution trace for the Playground UI.
    """
    # Mock return, normally we would load from JSONL or DB
    return {"trace_id": trace_id, "status": "completed"}

@router.post("/synthetic/generate")
async def generate_synthetic_data(count: int = 10):
    return generator.generate_tasks(count)

@router.get("/metrics/cost")
async def get_cost_analytics():
    return analytics.get_dashboard()
