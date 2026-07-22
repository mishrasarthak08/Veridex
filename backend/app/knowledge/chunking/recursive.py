from typing import List, Dict, Any
from .base import BaseChunker

class RecursiveCharacterChunker(BaseChunker):
    """
    Splits text recursively by character. A simple placeholder for a real 
    recursive text splitter.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: List[str] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively splits text."""
        final_chunks = []
        
        # Base case
        if len(text) <= self.chunk_size:
            return [text]

        separator = separators[-1]
        for s in separators:
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                break

        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        # Merge splits
        current_chunk = []
        current_length = 0

        for split in splits:
            if separator:
                split_len = len(split) + len(separator) if current_length > 0 else len(split)
            else:
                split_len = len(split)

            if current_length + split_len > self.chunk_size and current_length > 0:
                chunk_str = separator.join(current_chunk) if separator else "".join(current_chunk)
                if len(chunk_str) > self.chunk_size and len(separators) > 1:
                    # Recursive split if still too large
                    final_chunks.extend(self._split_text(chunk_str, separators[1:]))
                else:
                    final_chunks.append(chunk_str)
                
                # Start new chunk with overlap logic
                # We simplified overlap here for brevity: keep last few items from current_chunk if they fit
                while current_chunk:
                    overlap_len = len(separator.join(current_chunk)) if separator else len("".join(current_chunk))
                    if overlap_len <= self.chunk_overlap:
                        break
                    current_chunk.pop(0)
                
                current_chunk.append(split)
                current_length = len(separator.join(current_chunk)) if separator else len("".join(current_chunk))
            else:
                current_chunk.append(split)
                current_length += split_len

        if current_chunk:
            chunk_str = separator.join(current_chunk) if separator else "".join(current_chunk)
            if len(chunk_str) > self.chunk_size and len(separators) > 1:
                final_chunks.extend(self._split_text(chunk_str, separators[1:]))
            else:
                final_chunks.append(chunk_str)

        return final_chunks

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not text:
            return []
            
        metadata = metadata or {}
        raw_chunks = self._split_text(text, self.separators)
        
        chunks = []
        for i, raw_chunk in enumerate(raw_chunks):
            if raw_chunk.strip():
                chunks.append({
                    "text": raw_chunk.strip(),
                    "metadata": {**metadata, "chunk_index": i}
                })
            
        return chunks
