# Database Provider Selection

## Overview
This document outlines the scoring for our Managed PostgreSQL provider, transitioning away from the local Docker instance to support real traffic.

## Provider Scorecard

| Requirement | Supabase | AWS RDS | Google Cloud SQL |
| --- | --- | --- | --- |
| **Native Postgres** | Yes | Yes | Yes |
| **Built-in Connection Pooling** | Yes (PgBouncer) | Yes (RDS Proxy) | Yes (Cloud SQL Auth Proxy) |
| **Developer Experience** | High | Medium | Medium |
| **Out-of-the-box Auth & Storage** | Yes | No | No |
| **Point-in-Time Recovery (PITR)** | Yes (Pro plan+) | Yes | Yes |
| **Cost to Start** | Low (Free Tier) | Medium | Medium |

## Decision: **Supabase**

### Rationale
- **Speed to Market:** Supabase provides native PostgreSQL with PgBouncer pre-configured, drastically reducing infrastructure setup time.
- **Ecosystem:** Although we only need Postgres right now, having Edge Functions and Storage natively integrated provides an easy path if our requirements expand.
- **Cost:** Starts free, making it ideal for the current phase where traffic is minimal.
- **Alembic Compatibility:** Works perfectly with our existing Alembic migration setup via a direct connection string.
