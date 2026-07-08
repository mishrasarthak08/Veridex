from typing import List, Dict, Any
from .base import BaseChunker

class MarkdownChunker(BaseChunker):
    """
    Splits markdown by headers. Naive implementation for now.
    """
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not text:
            return []
            
        metadata = metadata or {}
        sections = text.split("\n## ")
        
        chunks = []
        for i, section in enumerate(sections):
            chunk_text = section if i == 0 else "## " + section
            chunks.append({
                "text": chunk_text.strip(),
                "metadata": {**metadata, "chunk_index": i, "chunk_type": "markdown_section"}
            })
            
        return chunks
