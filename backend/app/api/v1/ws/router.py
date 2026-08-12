from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
from app.ai.telemetry.tracker import tracker
from app.ai.swarm import swarm_engine

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass

manager = ConnectionManager()
swarm_engine.ws_manager = manager

@router.websocket("/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial timeline state
        await websocket.send_text(json.dumps({
            "type": "INIT",
            "data": [
                {
                    "message": e.message,
                    "time": e.time.isoformat(),
                    "type": e.type
                }
                for e in tracker.events
            ]
        }))
        
        last_count = len(tracker.events)
        while True:
            # Poll tracker for new events and broadcast
            # In a true pub/sub system, tracker would emit events to this manager.
            # For simplicity, we loop here.
            await asyncio.sleep(0.5)
            if len(tracker.events) > last_count:
                new_events = tracker.events[last_count:]
                last_count = len(tracker.events)
                for e in new_events:
                    await manager.broadcast({
                        "type": "NEW_EVENT",
                        "data": {
                            "message": e.message,
                            "time": e.time.isoformat(),
                            "type": e.type
                        }
                    })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
