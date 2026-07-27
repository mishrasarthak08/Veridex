from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging

from app.ai.events import ai_event_bus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/handshake", tags=["handshake"])

@router.post("/webhook")
async def handshake_webhook(request: Request):
    """
    Webhook endpoint to receive events from Handshake.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type", "unknown")
    logger.info(f"Received Handshake Webhook: {event_type}")

    # Emit the event onto the internal AI Event Bus
    await ai_event_bus.publish("HandshakeDataIngested", {
        "event_type": event_type,
        "payload": payload,
        "source": "webhook"
    })

    return {"status": "success", "message": "Event received and published"}
