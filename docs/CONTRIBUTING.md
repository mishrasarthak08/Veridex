# Contributing to Veridex

We welcome contributions! To ensure high quality, please follow these guidelines:

## The "Four Tests" Rule
Any new feature added to Veridex MUST pass the Four Tests:
1. **Designed**: Produce an Architecture Decision Record (ADR) in `docs/adr/`.
2. **Implemented**: Write the code cleanly using our base SDK abstractions.
3. **Measured**: Write load tests (`locustfile.py`) or benchmarks demonstrating performance.
4. **Operated**: Document chaos engineering/failure recovery in our runbooks.

## Local Development
1. Clone the repository.
2. Run `docker-compose up -d` for backing services.
3. Run `pytest` to ensure the core orchestrator tests pass before opening a PR.
