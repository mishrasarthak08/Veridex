from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from app.connectors.webhooks.manager import WebhookManager
from app.connectors.scheduler.engine import SyncScheduler

router = APIRouter()
webhook_manager = WebhookManager()
scheduler = SyncScheduler()

class SyncConfig(BaseModel):
    connector: str
    interval: int

@router.post("/webhooks/{source}")
async def handle_webhook(source: str, request: Request, background_tasks: BackgroundTasks):
    """
    Ingress point for all external webhooks (e.g. from GitHub, Slack).
    """
    payload = await request.json()
    background_tasks.add_task(webhook_manager.handle_payload, source, payload)
    return {"status": "accepted"}

@router.post("/schedule")
async def schedule_sync(config: SyncConfig):
    """
    Endpoint for the Sync Dashboard to configure polling intervals.
    """
    await scheduler.schedule_sync(config.connector, config.interval)
    return {"status": "scheduled", "connector": config.connector}

@router.get("/dashboard")
async def get_dashboard_metrics():
    """
    Returns metrics for the Sync Dashboard.
    """
    return {
        "connected_services": ["github", "slack", "notion"],
        "documents_indexed": 15420,
        "active_jobs": list(scheduler.jobs.keys()),
        "errors": 0
    }
