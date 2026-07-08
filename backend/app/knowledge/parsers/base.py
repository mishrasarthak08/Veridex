from typing import Dict, Any

class DocumentParser:
    """
    Parses normalized documents from the connector into semantic text blocks.
    In the future, this will wrap `unstructured` for PDFs, Word, etc.
    """
    def parse(self, document: Dict[str, Any]) -> str:
        # Currently we only process raw text/markdown from the filesystem connector.
        # This acts as a passthrough for now.
        return document.get("content", "")
