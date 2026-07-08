from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class JiraConnector(BaseConnector):
    name = "jira"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        return [{"key": "VER-123", "summary": "Fix login", "status": "To Do"}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("key") + ": " + raw_data.get("summary", ""),
            "content": raw_data.get("status", ""),
            "metadata": {"source": "jira"}
        }

    async def watch(self):
        pass
