# ADR 0003: Use Redis for Caching and Session Management

## Status
Accepted

## Context & Problem
As the platform scales, querying the primary database for every request (especially for authentication tokens, RBAC permissions, or rate-limiting) will become a bottleneck. We need a fast, in-memory data store to handle transient data, caching, and distributed locking.

## Options Considered
1. **Memcached**: Extremely fast and simple. However, it lacks advanced data structures (hashes, lists, sets) and persistence options.
2. **In-Memory Python Dicts**: Fast but not distributed. Fails when scaling out to multiple FastAPI worker processes or containers.
3. **Redis**: An open-source, in-memory data structure store, used as a database, cache, and message broker.

## Decision
We will use **Redis**.

## Tradeoffs
* **Pros**:
    * **Performance**: Sub-millisecond latency for read/write operations.
    * **Data Structures**: Supports strings, hashes, lists, sets, and sorted sets, making it highly versatile for rate-limiting, session management, and pub/sub.
    * **Ecosystem**: Industry standard with robust client libraries for Python.
* **Cons**:
    * Adds an additional piece of infrastructure to manage and monitor.
    * Data must fit in memory, requiring careful TTL (Time To Live) management and eviction policies.

## Consequences
Redis will be integrated early in the platform lifecycle to support:
1. Rate limiting.
2. Caching of relatively static data (e.g., User Roles/Permissions).
3. Temporary token blacklisting (if necessary).
We will use an async Python client (`redis.asyncio`) to interact with it from FastAPI.
