# LLM Orchestration Benchmark Report (Q3 2026)

## Executive Summary
This report analyzes the performance, cost, and reliability of running the Veridex Agent Orchestrator using GPT-4o, Claude-3.5-Sonnet, and local Llama-3-70B models.

## Methodology
- **Workload**: 1,000 parallel multi-step goals via locust.
- **Dataset**: Human-verified "Golden Set" of 100 enterprise tasks (code review, email summarization, data extraction).

## Results

| Model | Success Rate | Avg Latency (s) | Cost per 1k goals |
|---|---|---|---|
| Claude-3.5-Sonnet | 96% | 4.2 | $28.00 |
| GPT-4o | 94% | 3.8 | $35.00 |
| Llama-3-70B (Local) | 82% | 8.1 | $0.00 (Compute only)|

## Conclusion
Claude-3.5-Sonnet demonstrates the best cost-to-performance ratio for Veridex's specific internal Planner Agent prompts. We recommend updating `app/core/config.py` to route planner tasks to Anthropic by default, while routing simple extraction tasks to local Llama instances.
