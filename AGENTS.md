# Repository Guidelines

## Project Structure & Module Organization
- `src/api/`: FastAPI app (`main.py`) and request/response models.
- `src/agent/`: Guardian Agent core, clients (`clients/`), memory, and models.
- `src/config/`: Pydantic settings and env handling.
- `tests/`: Pytest suite (unit-focused); add new tests per feature.
- `docs/`: Architecture and deployment notes; update when APIs change.
- `deploy/`: Docker, Kubernetes, and Azure scripts/manifests for environments.

## Build, Test, and Development Commands
- `make install`: Create venv and install dependencies.
- `make run`: Run the API via `python main.py`.
- `make uvicorn`: Run with auto-reload at `http://localhost:8000`.
- `make test`: Execute tests with verbose output.
- `make coverage`: Run tests with coverage report.
- `make lint` / `make format`: Check style (flake8) / format (black).

## Coding Style & Naming Conventions
- Indentation: 4 spaces; keep lines concise and readable.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Use type hints for public functions; prefer explicit returns.
- Tools: Black (format), Flake8 (lint). Run before committing.

## Testing Guidelines
- Framework: Pytest; place tests in `tests/` named `test_*.py`.
- Scope: Unit tests for agent, API models, and clients; mock Legend services.
- Run locally: `pytest -v` or `make test`; add coverage for critical paths.

## Commit & Pull Request Guidelines
- Commits: Imperative mood; optional prefixes (`feat:`, `fix:`, `chore:`). Keep subjects <50 chars; explain “why” in body when needed.
- PRs: Clear description, linked issues (`Fixes #123`), test results, and any docs/diagram updates.
- Pre-flight: `make format && make lint && make test` must pass.

## Security & Configuration Tips
- Configuration via env vars (`src/config/settings.py`); use `.env` locally, never commit secrets.
- API uses Bearer tokens; set `VALID_API_KEYS` appropriately.
- Avoid logging sensitive data; prefer structured logs for errors.

For deeper architecture and workflows, see `CLAUDE.md`.
