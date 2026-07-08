# Agent Orchestration Cost Analysis

## The Problem
Multi-agent workflows are notoriously expensive. A single user goal ("Summarize the repository") can trigger 10+ sub-agents and hundreds of LLM calls.

## Findings
Our tracing telemetry (`app/observability/tracing`) revealed that 60% of our API costs were coming from the **Reflection Agent** re-evaluating context windows it had already seen.

## Optimization Applied
In PR #142, we implemented **Context Checkpointing**. Instead of passing the entire document history to the Reflection Agent, the Worker Agent now passes a synthesized summary graph.

- **Previous Cost per Workflow**: $0.42
- **New Cost per Workflow**: $0.18 (57% reduction)
