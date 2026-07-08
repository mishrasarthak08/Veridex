# ADR 0006: Declarative Policy Engine (YAML vs DB)

## Status
Accepted

## Context
We need to govern what tools an agent can execute on a per-tenant basis.

## Decision
We chose a **Declarative YAML Policy Engine (inspired by OPA)** over traditional database-backed RBAC rows.
- **Why**: AI policies are complex and often require "infrastructure-as-code" style reviews. By defining policies in YAML (e.g., `allow: [read_docs]`, `deny: [send_email]`), security teams can review policies in Git, and the application evaluates them instantly in-memory.

## Consequences
- **Positive**: Easy to audit, version-controllable, fast evaluation.
- **Negative**: Requires a deployment or config-map sync to update policies across all worker nodes.
