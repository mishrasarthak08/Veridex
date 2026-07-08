from fastapi import APIRouter
from app.schemas.common import success_response

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    # This will be replaced by actual prometheus_client logic later
    return success_response(data={"info": "Metrics endpoint stub"})
