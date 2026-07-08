import asyncio
import time
from typing import Dict, Any, AsyncGenerator, List, Optional
import httpx

from .base import BaseConnector

class SlackConnector(BaseConnector):
    def __init__(self, bot_token: str):
        """
        :param bot_token: Slack Bot Token (xoxb-...)
        """
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        self.workspace_id = None
        self.workspace_name = None

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/auth.test", headers=self.headers)
            data = response.json()
            if data.get("ok"):
                self.workspace_id = data.get("team_id", "unknown_team")
                self.workspace_name = data.get("team", "Unknown Workspace")
                return True
            return False

    async def _fetch_channels(self, client: httpx.AsyncClient) -> List[Dict]:
        channels = []
        next_cursor = None
        
        while True:
            payload = {"limit": 200, "types": "public_channel,private_channel"}
            if next_cursor:
                payload["cursor"] = next_cursor
                
            response = await client.post(f"{self.base_url}/conversations.list", headers=self.headers, json=payload)
            data = response.json()
            
            if not data.get("ok"):
                if data.get("error") == "ratelimited":
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    await asyncio.sleep(retry_after)
                    continue
                break
                
            for c in data.get("channels", []):
                # Only sync channels the bot is in, or we might get access denied on history
                if c.get("is_member", False):
                    channels.append(c)
                
            next_cursor = data.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break
                
        return channels

    async def _fetch_messages(self, client: httpx.AsyncClient, channel_id: str, oldest: str = None) -> AsyncGenerator[Dict, None]:
        next_cursor = None
        
        while True:
            payload = {"channel": channel_id, "limit": 100}
            if oldest:
                payload["oldest"] = oldest
            if next_cursor:
                payload["cursor"] = next_cursor
                
            response = await client.post(f"{self.base_url}/conversations.history", headers=self.headers, json=payload)
            data = response.json()
            
            if not data.get("ok"):
                if data.get("error") == "ratelimited":
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    await asyncio.sleep(retry_after)
                    continue
                break
                
            for msg in data.get("messages", []):
                # Ignore channel join/leave messages
                if msg.get("subtype") in ["channel_join", "channel_leave"]:
                    continue
                yield msg
                
                # If message has thread_ts and it's not a reply itself (fetch thread)
                if msg.get("thread_ts") == msg.get("ts") and msg.get("reply_count", 0) > 0:
                    async for reply in self._fetch_replies(client, channel_id, msg["ts"]):
                        if reply["ts"] != msg["ts"]: # don't yield the root message twice
                            yield reply
                
            next_cursor = data.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break
                
    async def _fetch_replies(self, client: httpx.AsyncClient, channel_id: str, thread_ts: str) -> AsyncGenerator[Dict, None]:
        next_cursor = None
        
        while True:
            payload = {"channel": channel_id, "ts": thread_ts, "limit": 100}
            if next_cursor:
                payload["cursor"] = next_cursor
                
            response = await client.post(f"{self.base_url}/conversations.replies", headers=self.headers, json=payload)
            data = response.json()
            
            if not data.get("ok"):
                if data.get("error") == "ratelimited":
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    await asyncio.sleep(retry_after)
                    continue
                break
                
            for reply in data.get("messages", []):
                yield reply
                
            next_cursor = data.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Fetches history of all joined channels."""
        if not self.workspace_id:
            await self.authenticate()
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            channels = await self._fetch_channels(client)
            
            for channel in channels:
                channel_id = channel["id"]
                async for msg in self._fetch_messages(client, channel_id):
                    yield {
                        "source_id": f"slack:{self.workspace_id}:{channel_id}:{msg['ts']}",
                        "raw_data": msg,
                        "channel_id": channel_id,
                        "channel_name": channel["name"]
                    }

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Incremental sync: Fetches history > last_sync (Unix timestamp)."""
        if not self.workspace_id:
            await self.authenticate()
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            channels = await self._fetch_channels(client)
            
            for channel in channels:
                channel_id = channel["id"]
                async for msg in self._fetch_messages(client, channel_id, oldest=last_sync):
                    yield {
                        "source_id": f"slack:{self.workspace_id}:{channel_id}:{msg['ts']}",
                        "raw_data": msg,
                        "channel_id": channel_id,
                        "channel_name": channel["name"]
                    }

    async def normalize(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Slack message to standard format."""
        msg = raw_payload["raw_data"]
        channel_id = raw_payload["channel_id"]
        channel_name = raw_payload["channel_name"]
        
        user_id = msg.get("user") or msg.get("bot_id", "unknown")
        text = msg.get("text", "")
        ts = msg.get("ts")
        thread_ts = msg.get("thread_ts")
        
        content = f"**Channel**: #{channel_name}\n**User**: {user_id}\n**Time**: {ts}\n\n{text}"
        
        metadata = {
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "user_id": user_id,
            "ts": ts,
            "thread_ts": thread_ts,
            "is_thread_reply": thread_ts is not None and thread_ts != ts
        }
        
        return {
            "id": raw_payload["source_id"],
            "title": f"Slack Message in #{channel_name} at {ts}",
            "content": content,
            "source": "slack_message",
            "source_metadata": metadata
        }
