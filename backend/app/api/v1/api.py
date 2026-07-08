from fastapi import APIRouter
from app.api.v1.auth.router import router as auth_router
from app.api.v1.health.router import router as health_router
from app.api.v1.metrics.router import router as metrics_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.agents import router as agents_router
from app.api.v1.connectors import router as connectors_router
from app.api.v1.observability import router as observability_router
from app.api.v1.governance import router as governance_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(connectors_router, prefix="/connectors", tags=["connectors"])
api_router.include_router(observability_router, prefix="/observability", tags=["observability"])
api_router.include_router(governance_router, prefix="/governance", tags=["governance"])
