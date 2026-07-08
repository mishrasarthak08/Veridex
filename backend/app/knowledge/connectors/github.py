import asyncio
import base64
from typing import Dict, Any, AsyncGenerator, Optional
import httpx

from .base import BaseConnector

class GitHubConnector(BaseConnector):
    def __init__(self, access_token: str, repository_full_name: str):
        """
        :param access_token: The GitHub OAuth access token.
        :param repository_full_name: e.g., "mishrasarthak08/Veridex"
        """
        self.access_token = access_token
        self.repo_name = repository_full_name
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.access_token and self.access_token != "dummy_token":
            self.headers["Authorization"] = f"Bearer {self.access_token}"

    async def authenticate(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/user", headers=self.headers)
            return response.status_code == 200

    async def _fetch_paginated(self, client: httpx.AsyncClient, url: str, params: Optional[Dict] = None) -> AsyncGenerator[Dict, None]:
        if params is None:
            params = {}
        params["per_page"] = 100
        
        while url:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                for item in data:
                    yield item
            else:
                yield data
                
            # Handle pagination via Link header
            link_header = response.headers.get("Link", "")
            url = None
            if "rel=\"next\"" in link_header:
                links = link_header.split(",")
                for link in links:
                    if "rel=\"next\"" in link:
                        url = link[link.find("<")+1:link.find(">")]
                        params = {} # params are already in the URL
                        break

    async def _get_repo_metadata(self, client: httpx.AsyncClient) -> Dict:
        response = await client.get(f"{self.base_url}/repos/{self.repo_name}", headers=self.headers)
        response.raise_for_status()
        return response.json()
        
    async def _get_file_content(self, client: httpx.AsyncClient, file_url: str) -> Optional[str]:
        response = await client.get(file_url, headers=self.headers)
        if response.status_code != 200:
            return None
        data = response.json()
        if data.get("encoding") == "base64" and data.get("content"):
            try:
                return base64.b64decode(data["content"]).decode("utf-8")
            except Exception:
                return None
        return None

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Yields repository metadata, files, issues, and PRs."""
        async with httpx.AsyncClient() as client:
            # 1. Repository Metadata
            repo = await self._get_repo_metadata(client)
            yield {
                "type": "repository",
                "source_id": f"github:{repo['id']}",
                "content": repo.get("description", "") or f"Repository {self.repo_name}",
                "metadata": {
                    "name": self.repo_name,
                    "url": repo.get("html_url"),
                    "stars": repo.get("stargazers_count"),
                    "language": repo.get("language")
                }
            }
            
            # 2. Files (using recursive tree to avoid multiple API calls for directories)
            default_branch = repo.get("default_branch", "main")
            tree_url = f"{self.base_url}/repos/{self.repo_name}/git/trees/{default_branch}?recursive=1"
            response = await client.get(tree_url, headers=self.headers)
            if response.status_code == 200:
                tree_data = response.json().get("tree", [])
                for item in tree_data:
                    # Only process blobs (files) and skip huge/binary ones if possible
                    if item["type"] == "blob":
                        # Basic extension filtering to avoid binary files
                        path = item["path"]
                        ext = path.split('.')[-1].lower() if '.' in path else ''
                        if ext in ['png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'zip', 'tar', 'gz']:
                            continue
                            
                        content = await self._get_file_content(client, item["url"])
                        if content:
                            yield {
                                "type": "file",
                                "source_id": f"github:{self.repo_name}:file:{path}",
                                "content": content,
                                "metadata": {
                                    "path": path,
                                    "url": f"{repo.get('html_url')}/blob/{default_branch}/{path}",
                                    "repo": self.repo_name
                                }
                            }
                            
            # 3. Issues and PRs
            issues_url = f"{self.base_url}/repos/{self.repo_name}/issues"
            async for issue in self._fetch_paginated(client, issues_url, {"state": "all"}):
                issue_type = "pull_request" if "pull_request" in issue else "issue"
                content = f"{issue.get('title', '')}\n\n{issue.get('body', '')}"
                yield {
                    "type": issue_type,
                    "source_id": f"github:{self.repo_name}:{issue_type}:{issue['number']}",
                    "content": content,
                    "metadata": {
                        "number": issue['number'],
                        "title": issue.get('title'),
                        "url": issue.get('html_url'),
                        "state": issue.get('state'),
                        "author": issue.get('user', {}).get('login')
                    }
                }

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Incremental sync: Fetches only recently updated issues/PRs and commits."""
        # Note: GitHub doesn't have an easy "files changed since X" endpoint without comparing commits.
        # For this connector, incremental sync will focus on Issues/PRs using the `since` parameter.
        async with httpx.AsyncClient() as client:
            issues_url = f"{self.base_url}/repos/{self.repo_name}/issues"
            params = {"state": "all", "since": last_sync}
            async for issue in self._fetch_paginated(client, issues_url, params):
                issue_type = "pull_request" if "pull_request" in issue else "issue"
                content = f"{issue.get('title', '')}\n\n{issue.get('body', '')}"
                yield {
                    "type": issue_type,
                    "source_id": f"github:{self.repo_name}:{issue_type}:{issue['number']}",
                    "content": content,
                    "metadata": {
                        "number": issue['number'],
                        "title": issue.get('title'),
                        "url": issue.get('html_url'),
                        "state": issue.get('state'),
                        "author": issue.get('user', {}).get('login')
                    }
                }

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert GitHub metadata to standard format."""
        obj_type = raw_data.get("type", "unknown")
        metadata = raw_data.get("metadata", {})
        
        title = metadata.get("title") or metadata.get("path") or metadata.get("name") or "Untitled GitHub Object"
        
        return {
            "id": raw_data["source_id"],
            "title": title,
            "content": raw_data["content"],
            "source": f"github_{obj_type}",
            "source_metadata": metadata
        }
