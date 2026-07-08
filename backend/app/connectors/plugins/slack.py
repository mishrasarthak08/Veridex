from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class SlackConnector(BaseConnector):
    name = "slack"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        return [{"id": "msg_1", "text": "Hello world", "channel": "general"}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": f"Message in {raw_data.get('channel')}",
            "content": raw_data.get("text", ""),
            "metadata": {"source": "slack"}
        }

    async def watch(self):
        pass
