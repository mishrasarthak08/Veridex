# ADR 0001: Use FastAPI for Backend Framework

## Status
Accepted

## Context & Problem
We need to select a framework for the Veridex platform backend. The backend will need to be highly performant, capable of asynchronous operations (for LLM streams, webhooks, DB calls), and easy to document since we will expose a robust API to both internal frontends and external integrations.

## Options Considered
1. **Django**: Excellent built-in admin, ORM, and "batteries-included" features. However, it can be monolithic and its async support, while improving, is still less native and ergonomic than newer frameworks.
2. **Flask**: Highly flexible and lightweight. However, it lacks built-in typing support, native async features (historically), and automatic API documentation.
3. **FastAPI**: Modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.

## Decision
We will use **FastAPI**.

## Tradeoffs
* **Pros**:
    * **Performance**: Built on Starlette and Pydantic, making it one of the fastest Python frameworks.
    * **Async Native**: Designed from the ground up for asynchronous programming, which is critical for AI workloads (streaming, external API calls).
    * **Auto-Documentation**: Automatically generates OpenAPI (Swagger) and ReDoc interfaces, which is essential for our API-first platform approach.
    * **Developer Experience**: Strong type hinting provides excellent IDE support and catches errors early.
* **Cons**:
    * **Less "Batteries-Included"**: Requires us to manually integrate an ORM (SQLAlchemy), migration tool (Alembic), authentication, and logging compared to Django.

## Consequences
We will need to carefully architect our application (see ADR 0004 on Layered Architecture) and manually wire up best practices for authentication, logging, and error handling, rather than relying on a framework's built-in conventions. We will strictly use Pydantic for validation and serialization.
