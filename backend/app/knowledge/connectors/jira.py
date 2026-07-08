import asyncio
import base64
from typing import Dict, Any, AsyncGenerator, List, Optional
import httpx

from .base import BaseConnector

class JiraConnector(BaseConnector):
    def __init__(self, jira_url: str, email: str, api_token: str):
        """
        :param jira_url: e.g., "https://your-domain.atlassian.net"
        :param email: Jira account email
        :param api_token: Jira API token
        """
        self.base_url = jira_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        
        auth_string = f"{self.email}:{self.api_token}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/rest/api/3/myself", headers=self.headers)
            return response.status_code == 200

    async def _fetch_paginated_jql(self, client: httpx.AsyncClient, jql: str) -> AsyncGenerator[Dict, None]:
        url = f"{self.base_url}/rest/api/3/search"
        start_at = 0
        max_results = 50
        
        while True:
            payload = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": ["summary", "description", "status", "priority", "issuetype", 
                           "assignee", "reporter", "labels", "created", "updated", 
                           "project", "customfield_10016", "customfield_10020", "customfield_10014", "issuelinks", "comment"], # customfields vary by Jira instance for Epic/Sprint, but we request common ones
                "expand": ["changelog", "renderedFields"]
            }
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("issues", [])
            for issue in issues:
                yield issue
                
            start_at += max_results
            if start_at >= data.get("total", 0):
                break

    async def _fetch_boards_and_sprints(self, client: httpx.AsyncClient) -> Dict:
        """Helper to fetch board/sprint hierarchy."""
        boards_url = f"{self.base_url}/rest/agile/1.0/board"
        structure = {}
        
        try:
            response = await client.get(boards_url, headers=self.headers, params={"maxResults": 50})
            if response.status_code == 200:
                boards = response.json().get("values", [])
                for b in boards:
                    b_id = str(b["id"])
                    structure[b_id] = {"name": b["name"], "project": b.get("location", {}).get("projectKey"), "sprints": {}}
                    
                    # Fetch sprints for board
                    sprints_url = f"{self.base_url}/rest/agile/1.0/board/{b_id}/sprint"
                    s_resp = await client.get(sprints_url, headers=self.headers)
                    if s_resp.status_code == 200:
                        sprints = s_resp.json().get("values", [])
                        for s in sprints:
                            structure[b_id]["sprints"][str(s["id"])] = s["name"]
        except Exception as e:
            print(f"Warning: Failed to fetch Agile Boards: {e}")
            
        return structure

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Fetches issues ordered by updated."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            boards_data = await self._fetch_boards_and_sprints(client)
            
            jql = "ORDER BY updated DESC"
            async for issue in self._fetch_paginated_jql(client, jql):
                yield {
                    "source_id": f"jira:{issue['key']}",
                    "raw_data": issue,
                    "boards_data": boards_data
                }

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Incremental sync using JQL updated."""
        # last_sync should be formatted like "2023-10-01 12:00" or we can just use a standard date format
        # If it's an ISO string, we might need to convert it to Jira's expected format (yyyy-MM-dd HH:mm)
        # We'll just pass it into JQL safely.
        async with httpx.AsyncClient(timeout=30.0) as client:
            boards_data = await self._fetch_boards_and_sprints(client)
            
            # Simple fallback if last_sync is not properly formatted for Jira
            jql = f'updated >= "{last_sync}" ORDER BY updated DESC'
            
            try:
                async for issue in self._fetch_paginated_jql(client, jql):
                    yield {
                        "source_id": f"jira:{issue['key']}",
                        "raw_data": issue,
                        "boards_data": boards_data
                    }
            except httpx.HTTPStatusError as e:
                # If JQL is invalid due to date parsing, fallback to a safer sync
                if e.response.status_code == 400:
                    jql = 'updated >= "-1d" ORDER BY updated DESC'
                    async for issue in self._fetch_paginated_jql(client, jql):
                        yield {
                            "source_id": f"jira:{issue['key']}",
                            "raw_data": issue,
                            "boards_data": boards_data
                        }
                else:
                    raise

    def _extract_text_from_adf(self, node: Dict) -> str:
        """Extracts text from Atlassian Document Format (v3 API)."""
        if not node:
            return ""
        if type(node) is str:
            return node
            
        text = ""
        if node.get("type") == "text":
            text += node.get("text", "")
            
        for child in node.get("content", []):
            text += self._extract_text_from_adf(child)
            if child.get("type") in ["paragraph", "heading"]:
                text += "\n\n"
        return text

    async def normalize(self, raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Jira Issue to standard format."""
        issue = raw_payload["raw_data"]
        boards_data = raw_payload.get("boards_data", {})
        fields = issue.get("fields", {})
        
        key = issue["key"]
        summary = fields.get("summary", "")
        
        # Jira v3 description is an ADF object, not plain text
        desc_obj = fields.get("description", {})
        description = self._extract_text_from_adf(desc_obj)
        
        status = fields.get("status", {}).get("name", "")
        priority = fields.get("priority", {}).get("name", "")
        issue_type = fields.get("issuetype", {}).get("name", "")
        
        assignee = fields.get("assignee", {})
        reporter = fields.get("reporter", {})
        assignee_id = assignee.get("accountId") if assignee else None
        reporter_id = reporter.get("accountId") if reporter else None
        
        project = fields.get("project", {})
        project_key = project.get("key")
        project_id = project.get("id")
        
        # Extract Comments
        comments_arr = fields.get("comment", {}).get("comments", [])
        comments_text = "\n".join([f"{c.get('author', {}).get('displayName', 'Unknown')}: {self._extract_text_from_adf(c.get('body', {}))}" for c in comments_arr])
        
        content = f"# {key}: {summary}\n\n**Type**: {issue_type} | **Status**: {status} | **Priority**: {priority}\n\n## Description\n{description}\n\n## Comments\n{comments_text}"
        
        # Extract Linked Issues
        blocks = []
        duplicates = []
        for link in fields.get("issuelinks", []):
            link_type = link.get("type", {}).get("name")
            if "outwardIssue" in link:
                target_key = link["outwardIssue"]["key"]
                if link_type == "Blocks":
                    blocks.append(target_key)
                elif link_type == "Duplicate":
                    duplicates.append(target_key)
            elif "inwardIssue" in link:
                target_key = link["inwardIssue"]["key"]
                if link_type == "Blocks":
                    blocks.append(target_key) # Adjust direction based on actual Jira usage
                
        metadata = {
            "key": key,
            "project_key": project_key,
            "project_id": project_id,
            "status": status,
            "priority": priority,
            "issue_type": issue_type,
            "assignee_id": assignee_id,
            "reporter_id": reporter_id,
            "labels": fields.get("labels", []),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "blocks": blocks,
            "duplicates": duplicates,
            "boards_data": boards_data # passing this down for the graph layer
        }
        
        return {
            "id": raw_payload["source_id"],
            "title": f"{key}: {summary}",
            "content": content,
            "source": "jira_issue",
            "source_metadata": metadata
        }
