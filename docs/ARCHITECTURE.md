# System Architecture

Veridex evolved over 10 development sprints to solve the core challenges of deploying AI into the enterprise.

## 1. The Gateway (API Layer)
FastAPI provides the ingress. The `APIGatewayMiddleware` intercepts traffic, validates the tenant API key against our Secrets provider (HashiCorp Vault/K8s), and enforces usage quotas.

## 2. Distributed Orchestration
We utilize a Task-Driven Multi-Agent pattern:
- **Planner Agent**: Decomposes a user goal into a DAG of sub-tasks.
- **Worker Agents**: Specialized agents (Researchers, Writers) pull tasks from Redis via Celery workers. 
- **Reflection**: Results are merged and critiqued before returning to the user.

## 3. Knowledge Layer
- **Ingestion**: The platform ingests markdown, PDFs, and codebases.
- **Vector DB**: Qdrant handles retrieval using **Hybrid Search** (Dense + Sparse/BM25 embeddings), achieving high MRR on code queries.

## 4. Observability & Telemetry
Every single LLM call generates a `TraceSpan`. We record latency, cost, and exact prompt versions. This feeds into our LLM-as-a-Judge evaluation pipeline to catch regressions.
