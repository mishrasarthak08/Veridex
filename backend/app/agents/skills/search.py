from .base import BaseSkill
from typing import Any

class SearchSkill(BaseSkill):
    name = "search_knowledge"
    description = "Searches the internal knowledge base for context."

    async def execute(self, query: str, limit: int = 5) -> Any:
        # In a real implementation, this would call the HybridRetriever from Sprint 3
        return [{"id": "doc_1", "text": f"Found info about {query}"}]
