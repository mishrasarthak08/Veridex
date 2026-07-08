from typing import List, Dict, Any

class ContextBuilder:
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens

    def build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Intelligently builds context from reranked chunks.
        Adds citations, removes duplicates, and respects token budgets.
        """
        context_parts = []
        current_tokens = 0
        seen_chunks = set()
        
        for i, doc in enumerate(documents):
            text = doc.get("text", "")
            if text in seen_chunks:
                continue
                
            seen_chunks.add(text)
            
            # Extremely rough token estimate (1 token ~= 4 chars)
            estimated_tokens = len(text) // 4
            
            if current_tokens + estimated_tokens > self.max_tokens:
                break
                
            source = doc.get("metadata", {}).get("filename", "Unknown Source")
            
            # Format with citation
            context_parts.append(f"[{i+1}] Source: {source}\n{text}\n")
            current_tokens += estimated_tokens
            
        return "\n".join(context_parts)
