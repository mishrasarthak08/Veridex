from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class GitHubConnector(BaseConnector):
    name = "github"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        # Mocked response
        return [{"id": "issue_1", "title": "Fix the bug", "type": "issue"}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title"),
            "content": raw_data.get("body", ""),
            "metadata": {"type": raw_data.get("type", "unknown")}
        }

    async def watch(self):
        pass
