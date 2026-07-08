# ADR 0005: Distributed Agent Orchestration (Redis vs Kafka)

## Status
Accepted

## Context
Veridex's agent orchestrator needed to transition from an in-process `asyncio` DAG to a distributed worker pool (Sprint 7 Epic 2). We evaluated Apache Kafka and Redis.

## Decision
We chose **Redis (via Celery)** as the message broker for the initial cloud-native transition.
- **Why**: Redis is already a core dependency for session management and rate limiting. Standing up a full Kafka/Zookeeper cluster adds significant operational overhead (memory and maintenance) that isn't justified by our current throughput requirements.
- We configured Celery with dedicated routing queues (`planner_queue`, `agent_queue`) which provides the independent scalability requested.

## Consequences
- **Positive**: Rapid deployment, lower infrastructure cost, native Python ecosystem integration.
- **Negative**: Redis is an in-memory datastore; if the Redis pod crashes without disk persistence, pending queued tasks are lost. We mitigate this with Kubernetes volume claims and client-side retries.
