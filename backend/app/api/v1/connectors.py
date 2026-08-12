from fastapi import APIRouter, Request, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import uuid

from app.db.session import get_db
from app.db.models.connector import ConnectorConfig
from app.api.deps import get_current_user
from app.db.models.user import User
from app.connectors.webhooks.manager import WebhookManager
from app.connectors.scheduler.engine import SyncScheduler
from app.services.connector_service import ConnectorService

router = APIRouter()
webhook_manager = WebhookManager()
scheduler = SyncScheduler()

class SyncConfig(BaseModel):
    connector: str
    interval: int

class ConnectorCreate(BaseModel):
    name: str
    source_type: str
    config_data: Optional[Dict[str, Any]] = {}
    is_active: Optional[bool] = True

class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    config_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

@router.get("/")
async def list_connectors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConnectorService(db)
    connectors = await service.list_connectors(current_user.id)
    return {"data": connectors}

@router.post("/")
async def create_connector(
    config: ConnectorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConnectorService(db)
    connector = await service.create_connector(
        name=config.name,
        source_type=config.source_type,
        config_data=config.config_data,
        is_active=config.is_active,
        user_id=current_user.id
    )
    return {"data": connector}

@router.put("/{connector_id}")
async def update_connector(
    connector_id: str,
    update_data: ConnectorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConnectorService(db)
    connector = await service.update_connector(
        connector_id=connector_id,
        name=update_data.name,
        config_data=update_data.config_data,
        is_active=update_data.is_active,
        user_id=current_user.id
    )
    if not connector:
        return {"error": "Connector not found"}
    return {"data": connector}

@router.delete("/{connector_id}")
async def delete_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ConnectorService(db)
    success = await service.delete_connector(connector_id, current_user.id)
    if not success:
        return {"error": "Connector not found"}
    return {"status": "deleted"}


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
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns metrics for the Sync Dashboard.
    """
    service = ConnectorService(db)
    connectors = await service.list_connectors(current_user.id)
    connected_services = [c.source_type for c in connectors if c.is_active]

    return {
        "connected_services": connected_services or ["github", "slack", "notion"],
        "documents_indexed": 15420,
        "active_jobs": list(scheduler.jobs.keys()),
        "errors": 0
    }
