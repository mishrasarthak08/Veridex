from typing import Dict, Any
from app.agents.communication.bus import AgentBus

class WebhookManager:
    """
    Validates and processes incoming webhooks, publishing them to the Agent Bus.
    """
    def __init__(self):
        self.bus = AgentBus()

    async def handle_payload(self, source: str, payload: Dict[str, Any]):
        """
        Normalizes the payload based on source, and publishes it.
        """
        print(f"[WebhookManager] Received payload from {source}")
        
        # In a real implementation, we would route to the appropriate connector's normalize() method
        normalized_event = {
            "source": source,
            "type": payload.get("action", "update"),
            "data": payload
        }
        
        await self.bus.publish(f"{source}.events", normalized_event)
        return {"status": "processed"}
