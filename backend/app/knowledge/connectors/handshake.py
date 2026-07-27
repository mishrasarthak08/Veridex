import logging
from typing import AsyncGenerator, Dict, Any, Optional
import httpx
from datetime import datetime, timezone

from .base import BaseConnector

logger = logging.getLogger(__name__)

class HandshakeConnector(BaseConnector):
    """
    Connector for pulling Job postings and Student Profiles from Handshake AI.
    """
    def __init__(self, api_token: str, base_url: str = "https://app.joinhandshake.com/api/v1"):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Token token={self.api_token}",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        """Test authentication by hitting the current user endpoint."""
        async with httpx.AsyncClient() as client:
            try:
                # Assuming /users/me is a valid ping endpoint
                response = await client.get(f"{self.base_url}/users/me", headers=self.headers)
                return response.status_code == 200
            except Exception as e:
                logger.error(f"Handshake authentication failed: {e}")
                return False

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch all jobs for a basic sync."""
        async with httpx.AsyncClient() as client:
            page = 1
            while True:
                response = await client.get(
                    f"{self.base_url}/postings",
                    headers=self.headers,
                    params={"page": page, "per_page": 50}
                )
                if response.status_code != 200:
                    break
                
                data = response.json()
                postings = data.get("postings", [])
                if not postings:
                    break
                
                for posting in postings:
                    yield posting
                
                page += 1

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Fetch jobs updated after the last_sync timestamp."""
        async with httpx.AsyncClient() as client:
            page = 1
            while True:
                response = await client.get(
                    f"{self.base_url}/postings",
                    headers=self.headers,
                    params={"updated_after": last_sync, "page": page, "per_page": 50}
                )
                if response.status_code != 200:
                    break
                
                data = response.json()
                postings = data.get("postings", [])
                if not postings:
                    break
                
                for posting in postings:
                    yield posting
                
                page += 1

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Handshake Job Posting payload to standard Veridex Document."""
        job_id = raw_data.get("id")
        title = raw_data.get("title", "Untitled Job")
        employer = raw_data.get("employer", {}).get("name", "Unknown Employer")
        description = raw_data.get("description", "")
        url = raw_data.get("url", "")
        
        # We synthesize a markdown body from the raw data
        content = f"# {title} at {employer}\n\n{description}"
        
        return {
            "document_id": f"handshake_job_{job_id}",
            "source_type": "handshake",
            "content": content,
            "metadata": {
                "title": title,
                "employer": employer,
                "url": url,
                "created_at": raw_data.get("created_at"),
                "updated_at": raw_data.get("updated_at")
            },
            "raw_data": raw_data,
            "permissions": ["public"] # Simplified access for public jobs
        }
