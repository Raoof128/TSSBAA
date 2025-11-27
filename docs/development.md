# Development Guide

This guide helps contributors work efficiently on the simulated 5G SBA Attack & Defence Lab.

## Prerequisites
- Python 3.11+
- Docker (for the composed lab)
- Make (optional, for shortcuts)

## Environment setup
```bash
# install dependencies
make install

# run lint + tests
make check
```

### Dev Containers
A ready-to-use [devcontainer](../.devcontainer/devcontainer.json) is provided. Open the repository in VS Code and choose **Reopen in Container** to get:
- Python 3.11 environment
- Ruff + Pylance extensions preinstalled
- `pip install -e .[dev]` executed automatically

## Running the stack
Use Docker Compose for a full sandbox:
```bash
make docker-up
```
This starts NRF, AMF, SMF, PCF, and a rogue SMF attack container. Bring it down with:
```bash
make docker-down
```

For local-only processes, see the quickstart in [README.md](../README.md) or the detailed steps in [docs/operations.md](operations.md).

## Coding standards
- Type hints and docstrings are required for public functions/classes.
- Keep simulations **safe** and offline.
- Validate inputs and log defensive decisions (authentication, slice checks, rate limits).
- Run `ruff format .` before committing.

## Tests
Pytest is configured with async support. Add tests under `tests/` and ensure coverage for new defences or monitoring rules.

## Continuous Integration
GitHub Actions (`.github/workflows/ci.yml`) runs linting and tests on pushes and pull requests. Keep the workflow green by matching the local `make check` results.

## Documentation
Update relevant files when changing behaviour:
- Quickstart or project layout: `README.md`
- Operational flows: `docs/operations.md`
- API contracts: `docs/api.md`
- Architecture or security posture: `docs/architecture.md`

## Safety reminder
All features must remain confined to the lab network. Do not introduce real network interactions, secrets, or RF manipulation.
