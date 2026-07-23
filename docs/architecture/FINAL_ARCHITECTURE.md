# Veridex 1.0.0 Final Architecture Overview

Veridex is a high-availability, multi-tenant enterprise AI agent orchestration platform. This document outlines the final v1.0.0 system architecture.

## 1. Core Services

### API Gateway (FastAPI)
The central nervous system of the platform. It handles all synchronous HTTP and WebSocket connections, enforces JWT authentication, and dispatches long-running background tasks.

### Agent Orchestrator (Celery/Redis)
All AI workflows are modeled as Directed Acyclic Graphs (DAGs) and executed asynchronously via Celery.
- **Planners**: Decompose complex user goals into sub-tasks.
- **Workers**: Execute specific sub-tasks (e.g., calling tools, hitting third-party APIs, semantic search).
- **Chaos & Retries**: Robust `@shared_task(max_retries=3)` blocks with exponential backoff ensure that LLM provider outages or broker downtime do not cause data loss.

### Knowledge Graph & Vector Store
We employ a hybrid retrieval approach:
- **Qdrant**: Stores dense vector embeddings of text chunks for semantic search.
- **Neo4j**: Stores the Knowledge Graph, linking documents to their sources, authors, and conceptual entities.
- **Postgres**: Serves as the primary source of truth for structured relational data (Users, Tenants, Workspaces).

## 2. Enterprise Governance & Security

### OPA-Style Policy Engine
Every action executed by an agent (e.g., executing a tool, accessing a database, generating a SQL query) passes through the `policy_engine.py`. This declarative framework ensures that an agent operating on behalf of Tenant A can never accidentally or maliciously access data belonging to Tenant B.

### Audit Ledger
All agent reasoning steps, tool payloads, and LLM responses are immutably logged into the Postgres `audit_logs` table for compliance and debugging.

## 3. Infrastructure & Deployment

### Kubernetes & Helm
Veridex is fully containerized. The provided Helm chart (`helm/veridex/`) allows operators to deploy the microservices (API, Workers, Policy Engine, Frontend) into separate, horizontally scalable pods, while stateful services (Postgres, Qdrant, Neo4j, MinIO, Redis) are managed via `StatefulSets`.

### Service Mesh (Istio)
An Istio VirtualService configuration sits in front of the application to intelligently manage traffic routing, load balancing across LLM providers, and circuit breaking in the event of upstream API volatility.

## 4. Evaluation (LLM-as-a-Judge)
Veridex ships with a built-in evaluation framework (`LLMJudge`). This uses a high-capacity LLM to automatically score the orchestrator's responses on Accuracy, Safety, and Conciseness, ensuring long-term prompt stability and guarding against behavioral drift.

---
*Built with ❤️ by the Veridex Engineering Team.*
