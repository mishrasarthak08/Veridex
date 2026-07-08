import hashlib
from typing import Dict, Any

def compute_checksum(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

class DocumentVersionTracker:
    """
    In a real system, this tracks version states in Postgres.
    """
    def __init__(self):
        # Placeholder dictionary
        self.versions = {}

    def is_modified(self, doc_id: str, content: str) -> bool:
        checksum = compute_checksum(content)
        if doc_id not in self.versions or self.versions[doc_id] != checksum:
            self.versions[doc_id] = checksum
            return True
        return False
