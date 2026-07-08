# ADR 0002: Use PostgreSQL for Primary Database

## Status
Accepted

## Context & Problem
The platform requires a primary relational database to store core business entities (Users, Organizations, Workspaces, Projects, Roles, Permissions). We need ACID compliance, robust querying capabilities, JSON support for flexible schemas, and high reliability.

## Options Considered
1. **MySQL / MariaDB**: Excellent relational databases, highly adopted. However, PostgreSQL typically offers better compliance with SQL standards and superior JSONB support.
2. **SQLite**: Lightweight and easy to set up. Unsuitable for a highly concurrent, production-grade platform.
3. **PostgreSQL**: Advanced, enterprise-class open-source relational database with strong community support and extensive features.

## Decision
We will use **PostgreSQL**.

## Tradeoffs
* **Pros**:
    * **Reliability and Data Integrity**: Fully ACID compliant.
    * **Advanced Types**: Native support for JSONB, Arrays, and UUIDs, allowing us to mix structured and semi-structured data when necessary.
    * **Ecosystem**: Excellent integration with SQLAlchemy, asyncpg (for async Python drivers), and analytics tools.
    * **Extensions**: Supports extensions like PostGIS and pgvector (if we chose to use it for vector search instead of a dedicated DB).
* **Cons**:
    * Requires proper connection pooling (e.g., PgBouncer) at scale to handle high connection counts compared to some NoSQL alternatives.

## Consequences
We will use `asyncpg` as our database driver to ensure non-blocking I/O in our FastAPI application. We will strictly define schemas using SQLAlchemy 2.0+ models and use Alembic for managing schema migrations.
