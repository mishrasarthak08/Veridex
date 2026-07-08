from app.connectors.sdk.base import BaseConnector
from typing import Dict, Any, List

class GmailConnector(BaseConnector):
    name = "gmail"

    async def authenticate(self) -> bool:
        return True

    async def sync(self) -> List[Dict[str, Any]]:
        return [{"id": "email_1", "subject": "Important Update", "body": "Please read."}]

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": raw_data.get("subject"),
            "content": raw_data.get("body", ""),
            "metadata": {"source": "gmail"}
        }

    async def watch(self):
        pass
