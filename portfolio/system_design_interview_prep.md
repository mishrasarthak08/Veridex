# System Design Interview Prep: Veridex

If asked to design an AI system in an interview, use Veridex as your mental model:

1. **Requirements & API Design**: Start with the Gateway (`FastAPI`). Discuss how `APIGatewayMiddleware` handles rate limits, tenant validation, and quotas before any AI processing begins.
2. **Data Model**: Mention the `MultiTenantBase` in SQLAlchemy to guarantee logical isolation.
3. **High-Level Design**: Draw the split between the synchronous API and the asynchronous Worker Pool (`Celery/Redis`). 
4. **Deep Dive (Knowledge)**: Explain why you chose Hybrid Search (Dense + Sparse/BM25 in Qdrant) over just Vector search. It handles exact keyword matches (like variable names) far better.
5. **Deep Dive (Reliability)**: Discuss how you use Istio VirtualServices for network retries against OpenAI/Anthropic, rather than muddying the application code with complex backoff loops.
6. **Observability**: Talk about your `ImmutableAuditLog` and execution tracing. Mention that "Companies don't deploy models because they are smart, they deploy them because they are measurable."
