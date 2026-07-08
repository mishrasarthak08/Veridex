from typing import List, Dict, Any
from .base import BaseChunker

class RecursiveCharacterChunker(BaseChunker):
    """
    Splits text recursively by character. A simple placeholder for a real 
    recursive text splitter.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not text:
            return []
            
        chunks = []
        metadata = metadata or {}
        
        # Extremely naive splitting for now
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "metadata": {**metadata, "chunk_index": len(chunks)}
            })
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks
