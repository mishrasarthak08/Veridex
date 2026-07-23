import httpx
from typing import Dict, Any

class KnowledgeClient:
    def __init__(self, client):
        self.client = client

    def sync_connector(self, connector_type: str, config: Dict[str, Any]) -> dict:
        """
        Triggers a background ingestion sync for a knowledge connector.
        """
        response = httpx.post(
            f"{self.client.base_url}/api/v1/connectors/sync",
            json={"type": connector_type, "config": config},
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()
