# Hybrid vs Vector Retrieval Benchmark

## Objective
To determine if adding a BM25 sparse index (Hybrid Search) to our Qdrant vector store improves Mean Reciprocal Rank (MRR) for code-heavy queries.

## Methodology
- **Index A**: Dense embeddings only (text-embedding-3-small).
- **Index B**: Hybrid (Dense + SPLADE sparse embeddings).
- **Queries**: 500 queries specifically searching for variable names and function signatures in a Python codebase.

## Results
| Strategy | MRR | P@5 |
|---|---|---|
| Dense Only | 0.62 | 0.71 |
| Hybrid | 0.89 | 0.94 |

## Architecture Decision
Based on these findings, we have updated `app/knowledge/qdrant_client.py` to unconditionally use Hybrid Search when indexing repositories. While it increases index size by 18%, the 43% boost to MRR on code queries is essential for the Developer Platform.
