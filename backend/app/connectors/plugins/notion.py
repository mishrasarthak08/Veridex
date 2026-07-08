from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class NotionConnector(BaseConnector):
    name = "notion"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        return [{"id": "page_1", "title": "Architecture Doc", "blocks": []}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title"),
            "content": str(raw_data.get("blocks", [])),
            "metadata": {"source": "notion"}
        }

    async def watch(self):
        pass
