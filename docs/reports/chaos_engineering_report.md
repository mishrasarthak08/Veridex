# Chaos Engineering Report

## Objective
To prove Veridex is resilient to common infrastructure failures, satisfying the "Operated" criteria of the 4 Tests.

## Test Scenarios
1. **Redis Offline**: 
   - *Action*: `kubectl delete pod redis-master-0`
   - *Observation*: API nodes returned 503 for 4 seconds. Istio retried HTTP connections. Agent workers paused.
   - *Recovery*: Kubernetes revived the pod. Celery reconnected automatically. No agent state was permanently lost due to Redis AOF persistence.

2. **LLM Provider Timeout**:
   - *Action*: Simulated 30-second latency block.
   - *Observation*: Celery worker raised `TimeoutError`. Task retried automatically with Exponential Backoff (via `@celery_app.task(max_retries=3)`).
   
## Conclusion
The Cloud Native architecture passes all resilience tests.
