# Pull Request Checklist

## Summary
- What does this change do and why?
- Any relevant context or alternatives considered?

## Linked Issues
- Fixes #
- Related #

## Changes
- [ ] User-facing/API changes (documented below)
- [ ] Internal refactor/cleanup
- [ ] Bug fix
- [ ] Feature

## Screenshots/Logs (if relevant)
<!-- Add before/after or logs for reviewers -->

## Breaking Changes
- [ ] Yes (describe migration/back-compat plan)
- [ ] No

## Testing Notes
- Added/updated tests for new behavior.
- Local verification steps:
  - `make install` (first-time setup)
  - `make test` (all tests pass)
  - `make uvicorn` or `make run` (manual check, if applicable)

## PR Checklist
- [ ] Clear description and rationale provided
- [ ] Linked issues included (e.g., `Fixes #123`)
- [ ] Tests added/updated and pass locally (`make test`)
- [ ] Coverage checked (`make coverage`), no significant regressions
- [ ] Lint and format pass (`make format && make lint`)
- [ ] Docs updated as needed (`docs/`, `AGENTS.md`), especially for API changes
- [ ] API models and FastAPI routes updated; OpenAPI docs verified
- [ ] Security: no secrets committed; uses env vars; avoids logging sensitive data
- [ ] Deployment manifests/scripts updated if required (`deploy/`)
- [ ] Backwards compatibility considered; migrations or notes provided

## Additional Notes
- Anything reviewers should pay special attention to?
