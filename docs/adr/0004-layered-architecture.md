# ADR 0004: Strict Layered Architecture

## Status
Accepted

## Context & Problem
FastAPI does not prescribe a specific project structure. In early stages, it is tempting to put database queries, business logic, and route handling all inside the router endpoints. As the application grows into a platform, this "fat controller" anti-pattern leads to code duplication, makes unit testing incredibly difficult, and prevents code reuse across different parts of the system (e.g., a background worker needing to use the same logic as an API endpoint).

## Options Considered
1. **"Fat Router" Architecture**: Put everything in the endpoint function. Easy to start, impossible to maintain.
2. **Django-style Apps**: Grouping by feature (e.g., `users/`, `projects/`). This is viable but can still blur the lines between DB access and business logic if not strictly enforced.
3. **Strict Layered (N-Tier) Architecture**: Separating concerns into Routers, Services, Repositories, and Models.

## Decision
We will adopt a **Strict Layered Architecture**.

## Structure & Responsibilities
1. **Routers (`api/v1/`)**: Handle HTTP requests/responses, path/query parameters, and delegate to Services. *No business logic or direct DB access.*
2. **Services (`services/`)**: Contain all core business logic. They orchestrate calls between different repositories and external APIs. They do not know about HTTP requests (FastAPI Request objects) or raw DB sessions.
3. **Repositories (`repositories/`)**: Encapsulate all database interaction (SQLAlchemy queries). They receive and return Domain Models. *No business logic.*
4. **Models (`db/models/`)**: SQLAlchemy definitions of database tables.
5. **Schemas (`schemas/`)**: Pydantic models for data validation, serialization, and API contracts.

## Tradeoffs
* **Pros**:
    * **Testability**: Services and Repositories can be unit tested in isolation using mocks, without needing a running database or FastAPI test client.
    * **Reusability**: A background worker (e.g., Celery/Temporal) can call a Service method without needing to hit an HTTP endpoint.
    * **Maintainability**: Clear boundaries make it easy for any engineer to know *where* code belongs.
* **Cons**:
    * **Boilerplate**: Requires writing more files and passing data between layers for simple CRUD operations.

## Consequences
Code reviews must enforce these boundaries. A Router attempting to use `session.execute()` directly must be rejected and refactored into a Repository call orchestrated by a Service.
