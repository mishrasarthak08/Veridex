import os
from pathlib import Path
from typing import Dict, Any, AsyncGenerator
from .base import BaseConnector

class FileSystemConnector(BaseConnector):
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    async def authenticate(self) -> bool:
        return self.root_dir.exists() and self.root_dir.is_dir()

    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = Path(root) / file
                # Skip hidden files
                if file.startswith("."):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    stat = file_path.stat()
                    yield {
                        "source_id": str(file_path),
                        "content": content,
                        "metadata": {
                            "filename": file,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "modified_at": stat.st_mtime
                        }
                    }
                except UnicodeDecodeError:
                    # Skip binary files for now
                    pass

    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        # For simplicity in Sprint 3, just do full sync
        async for doc in self.sync():
            yield doc

    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        # Already somewhat normalized in sync
        return {
            "id": raw_data["source_id"],
            "title": raw_data["metadata"]["filename"],
            "content": raw_data["content"],
            "source": "filesystem",
            "source_metadata": raw_data["metadata"]
        }
