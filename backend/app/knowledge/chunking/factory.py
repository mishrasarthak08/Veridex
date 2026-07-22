from typing import Dict, Any
from .base import BaseChunker
from .recursive import RecursiveCharacterChunker
from .markdown import MarkdownChunker
from .token import TokenChunker

class ChunkerFactory:
    @staticmethod
    def get_chunker(doc_type: str, **kwargs) -> BaseChunker:
        """
        Returns an appropriate chunker based on the document type.
        """
        if doc_type in ["markdown", "md"]:
            return MarkdownChunker(**kwargs)
        elif doc_type in ["slack_thread", "jira_ticket"]:
            # For these, token chunker or recursive character chunker works well
            # with specific separators if needed. We'll default to recursive.
            return RecursiveCharacterChunker(**kwargs)
        elif doc_type in ["code", "python", "js"]:
            # For code, splitting by functions/classes is ideal, but we can use 
            # recursive with code-specific separators like "\nclass ", "\ndef "
            separators = ["\nclass ", "\ndef ", "\nfunction ", "\n\n", "\n", " ", ""]
            return RecursiveCharacterChunker(separators=separators, **kwargs)
        else:
            # Default fallback
            return TokenChunker(**kwargs)
