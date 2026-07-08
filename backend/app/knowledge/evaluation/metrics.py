from typing import List

class RetrievalEvaluator:
    @staticmethod
    def calculate_recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        retrieved_k = retrieved_ids[:k]
        hits = sum(1 for doc_id in relevant_ids if doc_id in retrieved_k)
        return hits / len(relevant_ids) if relevant_ids else 0.0

    @staticmethod
    def calculate_mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        for rank, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                return 1.0 / (rank + 1)
        return 0.0
