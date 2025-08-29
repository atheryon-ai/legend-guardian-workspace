# Repository Guidelines

## Project Structure & Module Organization
- `src/api/`: FastAPI app (`main.py`) and request/response models.
- `src/agent/`: Guardian Agent core logic, `clients/`, memory, and models.
- `src/config/`: Pydantic settings, env parsing, and defaults.
- `tests/`: Pytest unit tests and fixtures.
- `docs/`: Architecture and deployment notes.
- `deploy/`: Docker, Kubernetes, and Azure manifests/scripts.

## Build, Test, and Development Commands
- `make install`: Create virtualenv and install dependencies.
- `make run`: Start API via `python main.py`.
- `make uvicorn`: Dev server with auto‑reload at `http://localhost:8000`.
- `make test`: Run pytest with verbose output.
- `make coverage`: Run tests with coverage report.
- `make lint` / `make format`: Lint with Flake8 / format with Black.
- Example: `make install && make uvicorn`

## Coding Style & Naming Conventions
- Indentation: 4 spaces; keep lines concise and readable.
- Naming: `snake_case` (modules/functions), `PascalCase` (classes), `UPPER_SNAKE` (constants).
- Use type hints for public functions; prefer explicit returns.
- Tools: Black for formatting, Flake8 for linting. Ensure both pass before PRs.

## Testing Guidelines
- Framework: Pytest; name tests `tests/test_*.py`.
- Scope: Unit tests for agent, API models, and clients; mock Legend services.
- Run: `pytest -v` or `make test`; focus on critical paths for coverage.

## Commit & Pull Request Guidelines
- Commits: Imperative mood; optional prefixes (`feat:`, `fix:`, `chore:`); subject <50 chars; include a brief "why" when helpful.
- PRs: Clear description, linked issues (e.g., `Fixes #123`), passing tests, and any doc updates (e.g., `docs/`, API changes).
- Pre‑flight: `make format && make lint && make test` must pass.

## Security & Configuration Tips
- Configure via env vars (`src/config/settings.py`); use a local `.env`. Never commit secrets.
- API uses Bearer tokens; set `VALID_API_KEYS` appropriately for local/dev.
- Avoid logging sensitive data; prefer structured error logs.

## Architecture Overview
- For deeper context and workflows, see `CLAUDE.md`.

