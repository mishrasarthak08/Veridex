# ADR 0004: Prompt Versioning Strategy

## Status
Accepted

## Context
As we scale our agentic capabilities, prompts become the "source code" of the application. Overwriting prompts in a SQL database leads to silent regressions and lack of auditability. We need a rigorous way to version, track, and rollback prompts.

## Decision
We will use a **GitOps-style YAML versioning system** for prompts.
- Prompts will be stored in `app/observability/prompts/storage` as `{name}_v{version}.yaml`.
- This ensures all prompts are committed to source control, reviewed via Pull Requests, and instantly rollbackable.
- A/B experiments will specify the exact version string rather than querying a database row.

## Consequences
### Positive
- Strict audit log via Git history.
- Easy to review prompt changes in GitHub PRs alongside Python code changes.
- Safe rollbacks.

### Negative
- Requires a deployment to update a prompt (cannot hot-swap in production via a UI without triggering a Git commit). We accept this tradeoff for stability.
