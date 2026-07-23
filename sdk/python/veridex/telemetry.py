import httpx
from typing import List, Dict, Any

class TelemetryClient:
    def __init__(self, client):
        self.client = client

    def list_traces(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of traces from the backend.
        """
        response = httpx.get(
            f"{self.client.base_url}/api/v1/telemetry/",
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()
