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

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []
            
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_n = np.argsort(scores)[::-1][:limit]
        
        results = []
        for idx in top_n:
            if scores[idx] > 0:
                result = self.corpus[idx].copy()
                result["sparse_score"] = float(scores[idx])
                results.append(result)
                
        return results
