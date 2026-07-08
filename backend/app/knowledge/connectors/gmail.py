import asyncio
import base64
import time
from typing import Dict, Any, AsyncGenerator, Optional
import httpx

from app.core.config import settings
from .base import BaseConnector

class GmailConnector(BaseConnector):
    def __init__(self, access_token: str, refresh_token: str = None):
        """
        :param access_token: The Google OAuth access token.
        :param refresh_token: The Google OAuth refresh token (for auto-refresh).
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://gmail.googleapis.com/gmail/v1/users/me"
        self._update_headers()

    def _update_headers(self):
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    async def _refresh_access_token(self):
        if not self.refresh_token:
            raise Exception("Access token expired and no refresh token available.")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data["access_token"]
            self._update_headers()

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/profile", headers=self.headers)
            if response.status_code == 401 and self.refresh_token:
                try:
                    await self._refresh_access_token()
                    response = await client.get(f"{self.base_url}/profile", headers=self.headers)
                except Exception:
                    return False
            return response.status_code == 200

    def _extract_body(self, payload: Dict) -> str:
        """Recursively extracts plain text body from the payload."""
        if not payload:
            return ""
            
        mime_type = payload.get("mimeType")
        body_data = payload.get("body", {}).get("data")
        
        if mime_type == "text/plain" and body_data:
            try:
                # Gmail uses urlsafe base64
                return base64.urlsafe_b64decode(body_data).decode("utf-8")
            except Exception:
                pass
                
        # If multipart, look for text/plain part
        if "parts" in payload:
            for part in payload["parts"]:
                extracted = self._extract_body(part)
                if extracted:
                    return extracted
                    
        # Fallback to HTML if no plain text
        if mime_type == "text/html" and body_data:
             try:
                 return base64.urlsafe_b64decode(body_data).decode("utf-8")
             except Exception:
                 pass
                 
        return ""

    async def _fetch_messages(self, client: httpx.AsyncClient, params: Dict) -> AsyncGenerator[Dict, None]:
        url = f"{self.base_url}/messages"
        
        while True:
            response = await client.get(url, headers=self.headers, params=params)
            
            if response.status_code == 401:
                await self._refresh_access_token()
                response = await client.get(url, headers=self.headers, params=params)
                
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            for msg_meta in messages:
                msg_id = msg_meta["id"]
                msg_resp = await client.get(f"{self.base_url}/messages/{msg_id}?format=full", headers=self.headers)
                if msg_resp.status_code == 200:
                    yield msg_resp.json()
            
            next_page = data.get("nextPageToken")
            if not next_page:
                break
            params["pageToken"] = next_page

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Fetches all messages (could be huge, so we paginate)."""
        async with httpx.AsyncClient() as client:
            params = {"maxResults": 50}
            async for msg in self._fetch_messages(client, params):
                yield msg

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Incremental sync using 'after' query."""
        # Convert last_sync (ISO format or timestamp) to seconds
        # For simplicity, assuming last_sync is a unix timestamp string
        try:
            timestamp = int(float(last_sync))
        except ValueError:
            # fallback if it's not a timestamp
            timestamp = int(time.time()) - 86400 # last 24 hours
            
        async with httpx.AsyncClient() as client:
            params = {"maxResults": 50, "q": f"after:{timestamp}"}
            async for msg in self._fetch_messages(client, params):
                yield msg

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Gmail API message to standard format."""
        headers = raw_data.get("payload", {}).get("headers", [])
        
        header_map = {h["name"].lower(): h["value"] for h in headers}
        
        subject = header_map.get("subject", "No Subject")
        sender = header_map.get("from", "Unknown")
        recipients = header_map.get("to", "")
        date = header_map.get("date", "")
        
        body = self._extract_body(raw_data.get("payload", {}))
        
        # Build metadata
        metadata = {
            "message_id": raw_data.get("id"),
            "thread_id": raw_data.get("threadId"),
            "labels": raw_data.get("labelIds", []),
            "snippet": raw_data.get("snippet", ""),
            "sender": sender,
            "recipients": recipients,
            "date": date,
            "subject": subject
        }
        
        # We append headers for clarity in content
        content = f"From: {sender}\nTo: {recipients}\nDate: {date}\nSubject: {subject}\n\n{body}"
        
        return {
            "id": f"gmail:{raw_data.get('id')}",
            "title": subject,
            "content": content,
            "source": "gmail_email",
            "source_metadata": metadata
        }
