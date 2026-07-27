import re
from typing import List, Dict, Any
from .base import BaseChunker

class HandshakeChunker(BaseChunker):
    """
    Chunker optimized for Handshake job postings which often contain structured 
    sections (e.g., 'Requirements', 'Responsibilities').
    """
    def __init__(self, max_chunk_size: int = 1000):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if metadata is None:
            metadata = {}
            
        chunks = []
        
        # A simple heuristic: split by double newlines representing paragraphs or sections
        sections = re.split(r'\n\s*\n', text.strip())
        
        current_chunk = ""
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # If adding this section exceeds max size, save current chunk and start new one
            if len(current_chunk) + len(section) > self.max_chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": {**metadata}
                })
                current_chunk = section
            else:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section
                    
        # Add the last chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {**metadata}
            })
            
        return chunks
