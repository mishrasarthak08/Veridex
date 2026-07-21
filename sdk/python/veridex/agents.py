import httpx
from httpx_sse import connect_sse
import json
from typing import Iterator

class AgentClient:
    def __init__(self, client):
        self.client = client

    def run(self, goal: str, tenant_id: str = "default") -> dict:
        """
        Runs an agent workflow by hitting the /goal endpoint.
        """
        response = httpx.post(
            f"{self.client.base_url}/api/v1/agents/goal",
            json={"goal": goal},
            headers={"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        )
        response.raise_for_status()
        return response.json()

    def stream_timeline(self) -> Iterator[dict]:
        """
        Streams the execution timeline from the backend SSE endpoint.
        """
        headers = {"Authorization": f"Bearer {self.client.api_key}"} if self.client.api_key else {}
        with httpx.Client() as client:
            with connect_sse(client, "GET", f"{self.client.base_url}/api/v1/agents/timeline", headers=headers) as event_source:
                for sse in event_source.iter_sse():
                    try:
                        data = json.loads(sse.data)
                        yield {"event": sse.event, "data": data}
                    except json.JSONDecodeError:
                        yield {"event": sse.event, "data": sse.data}
