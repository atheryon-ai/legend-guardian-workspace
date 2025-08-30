---
name: Feature request
about: Propose an enhancement or new capability
labels: enhancement
assignees: ""
---

## Problem Statement
What problem or limitation does this address? Who is affected?

## Proposed Solution
Describe the desired behavior. Include API/CLI changes, new modules, or data models.

## Alternatives Considered
Other options you evaluated and why they aren’t preferred.

## Scope & Impact
- Affected areas (e.g., `src/api`, `src/agent`, `src/config`, `deploy/`):
- Backward compatibility: breaking/non-breaking (explain if breaking)

## API / Schema Changes
- New/updated FastAPI routes or models
- OpenAPI updates needed?

## Security & Configuration
- New env vars or secrets?
- Security considerations (tokens, PII, logging)

## Testing Strategy
- Unit tests to add/update (paths, cases)
- Manual verification steps (`make uvicorn`, curl examples)

## Deployment Notes
- Changes to Docker/Kubernetes/Azure manifests (`deploy/`)

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Additional Context
Links, mockups, or prior art.

## Requester Checklist
- [ ] Clearly defined problem and scope
- [ ] Considered alternatives and risks
- [ ] Documented API/Docs impact
