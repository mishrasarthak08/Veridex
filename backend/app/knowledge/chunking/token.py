import tiktoken
from typing import List, Dict, Any
from .base import BaseChunker

class TokenChunker(BaseChunker):
    """
    Splits text recursively by token count using tiktoken.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, model_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.tokenizer = tiktoken.get_encoding(model_name)
        except ValueError:
            self.tokenizer = tiktoken.encoding_for_model(model_name)

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not text:
            return []
            
        chunks = []
        metadata = metadata or {}
        
        tokens = self.tokenizer.encode(text)
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append({
                "text": chunk_text,
                "metadata": {**metadata, "chunk_index": len(chunks)}
            })
            start += (self.chunk_size - self.chunk_overlap)
            
        return chunks
