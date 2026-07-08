import asyncio
from typing import Dict, Any, AsyncGenerator, List, Optional
import httpx

from app.core.config import settings
from .base import BaseConnector

class NotionConnector(BaseConnector):
    def __init__(self, integration_token: str):
        """
        :param integration_token: The Notion Internal Integration Token.
        """
        self.token = integration_token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/me", headers=self.headers)
            return response.status_code == 200

    async def _fetch_blocks(self, client: httpx.AsyncClient, block_id: str) -> str:
        """Recursively fetch and parse blocks into markdown."""
        url = f"{self.base_url}/blocks/{block_id}/children"
        content = ""
        has_more = True
        next_cursor = None
        
        while has_more:
            params = {"page_size": 100}
            if next_cursor:
                params["start_cursor"] = next_cursor
                
            response = await client.get(url, headers=self.headers, params=params)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                await asyncio.sleep(retry_after)
                continue
                
            if response.status_code != 200:
                break
                
            data = response.json()
            for block in data.get("results", []):
                content += self._parse_block(block)
                # If block has children, recursively fetch them
                if block.get("has_children"):
                    child_content = await self._fetch_blocks(client, block["id"])
                    # Indent children
                    indented = "\n".join([f"    {line}" for line in child_content.split("\n") if line])
                    content += f"{indented}\n"
                    
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        return content

    def _parse_block(self, block: Dict) -> str:
        """Parses a Notion block into a markdown string."""
        b_type = block.get("type")
        if not b_type or b_type not in block:
            return ""
            
        b_data = block[b_type]
        text_arr = b_data.get("rich_text", [])
        
        # Extract plain text from rich_text array
        text = "".join([t.get("plain_text", "") for t in text_arr])
        
        if b_type == "paragraph":
            return f"{text}\n\n"
        elif b_type == "heading_1":
            return f"# {text}\n\n"
        elif b_type == "heading_2":
            return f"## {text}\n\n"
        elif b_type == "heading_3":
            return f"### {text}\n\n"
        elif b_type == "bulleted_list_item":
            return f"* {text}\n"
        elif b_type == "numbered_list_item":
            return f"1. {text}\n"
        elif b_type == "to_do":
            checked = "x" if b_data.get("checked") else " "
            return f"- [{checked}] {text}\n"
        elif b_type == "toggle":
            return f"<details><summary>{text}</summary>\n"
        elif b_type == "code":
            lang = b_data.get("language", "")
            return f"```{lang}\n{text}\n```\n\n"
        elif b_type == "quote":
            return f"> {text}\n\n"
        elif b_type == "callout":
            icon = b_data.get("icon", {}).get("emoji", "")
            return f"> {icon} {text}\n\n"
        elif b_type == "divider":
            return "---\n\n"
        else:
            # Fallback for tables, child_page, etc.
            return f"{text}\n" if text else ""

    async def _extract_title(self, properties: Dict) -> str:
        for prop_name, prop_val in properties.items():
            if prop_val.get("type") == "title":
                title_arr = prop_val.get("title", [])
                return "".join([t.get("plain_text", "") for t in title_arr])
        return "Untitled"

    async def _search_notion(self, client: httpx.AsyncClient, filter_params: Dict = None) -> AsyncGenerator[Dict, None]:
        url = f"{self.base_url}/search"
        payload = {"page_size": 100}
        
        if filter_params:
            payload.update(filter_params)
            
        has_more = True
        next_cursor = None
        
        while has_more:
            if next_cursor:
                payload["start_cursor"] = next_cursor
                
            response = await client.post(url, headers=self.headers, json=payload)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "1"))
                await asyncio.sleep(retry_after)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            for result in data.get("results", []):
                yield result
                
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
            # Rate limit backoff for search
            await asyncio.sleep(0.34) # Max ~3 requests per second

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Fetches all pages and databases."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            async for item in self._search_notion(client):
                obj_id = item["id"]
                obj_type = item["object"]
                
                # We fetch blocks only for pages to get their content
                content = ""
                if obj_type == "page":
                    content = await self._fetch_blocks(client, obj_id)
                    
                title = await self._extract_title(item.get("properties", {}))
                
                yield {
                    "source_id": f"notion:{obj_id}",
                    "type": obj_type,
                    "title": title,
                    "content": content,
                    "raw_data": item
                }

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Incremental sync: Notion search allows sorting by last_edited_time."""
        # For a truly robust incremental sync with Notion, we sort search by last_edited_time descending,
        # yield items, and stop once we hit an item older than last_sync.
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            sort_params = {
                "sort": {
                    "direction": "descending",
                    "timestamp": "last_edited_time"
                }
            }
            
            async for item in self._search_notion(client, filter_params=sort_params):
                item_edited = item.get("last_edited_time", "")
                if item_edited < last_sync:
                    break # We've reached older items
                    
                obj_id = item["id"]
                obj_type = item["object"]
                
                content = ""
                if obj_type == "page":
                    content = await self._fetch_blocks(client, obj_id)
                    
                title = await self._extract_title(item.get("properties", {}))
                
                yield {
                    "source_id": f"notion:{obj_id}",
                    "type": obj_type,
                    "title": title,
                    "content": content,
                    "raw_data": item
                }

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Notion metadata to standard format."""
        notion_obj = raw_data["raw_data"]
        
        parent = notion_obj.get("parent", {})
        parent_type = parent.get("type", "workspace")
        parent_id = parent.get(parent_type) if parent_type != "workspace" else "workspace"
        
        last_edited_by = notion_obj.get("last_edited_by", {}).get("id", "unknown")
        
        metadata = {
            "notion_id": notion_obj["id"],
            "url": notion_obj.get("url", ""),
            "parent_type": parent_type,
            "parent_id": parent_id,
            "last_edited_time": notion_obj.get("last_edited_time"),
            "last_edited_by": last_edited_by,
            "type": raw_data["type"]
        }
        
        return {
            "id": raw_data["source_id"],
            "title": raw_data["title"],
            "content": raw_data["content"] or raw_data["title"], # Databases might not have block content
            "source": "notion_page",
            "source_metadata": metadata
        }
