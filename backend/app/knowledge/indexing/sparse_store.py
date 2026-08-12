from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import numpy as np

class BM25SparseStore:
    """
    In-memory BM25 store for testing. 
    In production, this would be backed by Elasticsearch or OpenSearch.
    """
    def __init__(self):
        self.corpus: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25 = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        for doc in documents:
            text = doc.get("text", "")
            tokens = text.lower().split()
            self.corpus.append(doc)
            self.tokenized_corpus.append(tokens)
            
        # Re-build BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, limit: int = 5, metadata_filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
            
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Sort scores and indices
        sorted_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in sorted_indices:
            if scores[idx] <= 0:
                continue
                
            doc = self.corpus[idx]
            
            # Apply metadata filters (tenant_id)
            if metadata_filters:
                match = True
                for k, v in metadata_filters.items():
                    if doc.get(k) != v and doc.get("payload", {}).get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            result = doc.copy()
            result["sparse_score"] = float(scores[idx])
            results.append(result)
            
            if len(results) >= limit:
                break
                
        return results
