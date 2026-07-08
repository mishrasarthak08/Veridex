from fastapi import APIRouter
from app.schemas.common import success_response

router = APIRouter()

@router.get("/health")
async def health_check():
    return success_response(data={"status": "ok"})

@router.get("/ready")
async def readiness_check():
    # In the future, check DB and Redis connection
    return success_response(data={"status": "ready"})

@router.get("/live")
async def liveness_check():
    return success_response(data={"status": "alive"})
