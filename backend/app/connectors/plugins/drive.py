from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class DriveConnector(BaseConnector):
    name = "drive"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        return [{"id": "doc_1", "name": "Q2 Planning", "mimeType": "application/vnd.google-apps.document"}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("name"),
            "content": "Simulated extracted text from doc...",
            "metadata": {"source": "drive"}
        }

    async def watch(self):
        pass
