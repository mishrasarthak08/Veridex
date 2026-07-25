import httpx
from typing import List, Dict, Any

class ProjectsClient:
    def __init__(self, client):
        self.client = client

    def list_projects(self) -> Dict[str, Any]:
        """
        Retrieves a list of projects from the backend.
        """
        response = httpx.get(
            f"{self.client.base_url}/api/v1/projects/",
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()
