from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base import BaseChunker

class RecursiveCharacterChunker(BaseChunker):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        chunks = self.splitter.split_text(text)
        return [{"text": chunk, "metadata": metadata or {}} for chunk in chunks]
