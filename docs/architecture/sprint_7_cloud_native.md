# Architecture: Cloud Native Distributed Agent Runtime

## Objective
The transition of Veridex from a monolith to a distributed system capable of scaling individual agent pools dynamically.

## Core Components
1. **Kubernetes Control Plane**: `Helm` configurations dictate the deployment and autoscaling strategies. We utilize an HPA (Horizontal Pod Autoscaler) bound to 70% CPU target utilization.
2. **Service Mesh (Istio)**: VirtualServices handle transparent traffic shaping, injecting retries on `503 Unavailable` from LLM providers, avoiding application-level retry bloat.
3. **Distributed Worker Pool (Celery + Redis)**:
   - `planner_queue`: Handles goal decomposition.
   - `agent_queue`: Handles heavy LLM inference and tool usage.
   - This decouples the API gateway latency from the heavy AI operations.

## Chaos & Recovery
Our automated scripts regularly target Redis, Qdrant, and Worker pools with synthetic crashes. The Istio VirtualService configuration combined with Celery's `max_retries=3` on tasks guarantees fault-tolerance.
