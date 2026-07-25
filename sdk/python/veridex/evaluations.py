import httpx
from typing import List, Dict, Any

class EvaluationsClient:
    def __init__(self, client):
        self.client = client

    def list_evaluations(self) -> List[Dict[str, Any]]:
        response = httpx.get(
            f"{self.client.base_url}/api/v1/evaluations/",
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()

    def run_evaluations(self) -> Dict[str, Any]:
        response = httpx.post(
            f"{self.client.base_url}/api/v1/evaluations/run",
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()
