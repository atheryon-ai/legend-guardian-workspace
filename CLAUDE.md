# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL DEPLOYMENT PRINCIPLE

**USE ONLY OPEN SOURCE FINOS LEGEND COMPONENTS WITH OUT-OF-THE-BOX CONFIGURATION**

This project focuses exclusively on deploying the official FINOS Legend platform using:
- Official FINOS Docker images from Docker Hub (finos/legend-*)
- Standard configuration files from FINOS Legend repositories
- Out-of-the-box deployment patterns from FINOS documentation
- No custom modifications to core Legend services

When in doubt, always refer to:
1. Official FINOS Legend repositories on GitHub
2. FINOS Legend Docker Hub images
3. Standard Legend configuration examples

## High-Level Architecture

Legend Guardian Workspace is a Docker-based deployment of the FINOS Legend platform that orchestrates multiple microservices through Docker Compose profiles. The architecture follows a profile-based deployment strategy where services can be selectively enabled based on requirements.

### Service Dependencies Chain
```
setup → mongodb → (engine, sdlc, depot-store) → (studio, query, depot)
```

The `setup` service generates all necessary configuration files in the `z_generated` directory before other services start.

## Key Development Commands

### Primary Deployment Commands
```bash
# Navigate to deployment directory
cd deploy/docker-finos-official

# One-time setup (required first time)
./run-legend.sh setup up

# Deploy core Legend Studio stack
./run-legend.sh studio up -d

# Deploy full stack with Query
./run-legend.sh query up -d

# Service management
./run-legend.sh <profile> ps         # Check status
./run-legend.sh <profile> logs -f    # View logs
./run-legend.sh <profile> down       # Stop services
./run-legend.sh <profile> restart    # Restart services
```

### Available Profiles
- `setup` - Configuration generation service
- `engine` - Core Legend Engine (port 6300)
- `sdlc` - Source control management (port 6100)
- `studio` - Web UI (port 9000)
- `depot` - Model repository (port 6200)
- `query` - Data query interface (port 9001)
- `postgres` - PostgreSQL database

### Secret Configuration
```bash
# Configure GitLab OAuth (required)
cp .env.example .env.local
# Edit .env.local with GITLAB_APP_ID and GITLAB_APP_SECRET

# Alternative: Use interactive setup
deploy/secrets/setup.sh --env local --interactive
```

### Testing and Validation
```bash
# Lint Mermaid diagrams
npm run lint:mermaid

# Lint Markdown files
npm run lint:markdown

# Run all linting
npm run lint

# Verify service endpoints
curl http://localhost:6300/api/server/v1/info  # Engine
curl http://localhost:6100/api/info            # SDLC
curl http://localhost:9000/studio              # Studio
curl http://localhost:6200/depot               # Depot
```

## Project Structure

### Deployment Configuration
- `deploy/docker-finos-official/` - Main deployment directory
  - `run-legend.sh` - Primary deployment script with secrets integration
  - `docker-compose.yml` - Official FINOS Legend service definitions
  - `setup.sh` - Configuration file generator
  - `.env` - Service configuration variables
  - `z_generated/` - Auto-generated configuration files (created by setup)

### Environment Files
- `.env.local` - Local environment secrets (GitLab OAuth)
- `.env.example` - Template for environment variables
- `deploy/docker-finos-official/.env` - Service configuration

## Service Port Mapping

| Service | Port | Purpose |
|---------|------|---------|
| Legend Engine | 6300 | Core execution engine |
| Legend SDLC | 6100 | Source control management |
| Legend Studio | 9000 | Web UI |
| Legend Depot | 6200 | Model repository |
| Legend Query | 9001 | Data query interface |
| MongoDB | 27017 | Primary database |
| PostgreSQL | 5432 | Additional database |

## Configuration Flow

1. **Secrets Setup**: GitLab OAuth credentials stored in `.env.local`
2. **run-legend.sh**: Sources secrets and exports to Docker Compose
3. **setup service**: Generates configuration files in `z_generated/`
4. **Service startup**: Each service mounts its config from `z_generated/`

## Important Patterns

1. **Always use official images**: Never build custom Legend service images
2. **Minimal configuration**: Start with FINOS defaults, change only what's necessary
3. **Use run-legend.sh**: Always use the deployment script for consistency
4. **Profile-based deployment**: Use Docker Compose profiles for service combinations
5. **Configuration generation**: The setup service must run before other services

## Troubleshooting Common Issues

### OAuth Authentication Failures
1. Verify GITLAB_APP_ID and GITLAB_APP_SECRET in `.env.local`
2. Check GitLab OAuth app has "Confidential" checked
3. Ensure redirect URIs match exactly: `http://localhost:6100/api/auth/callback`
4. Clear browser cookies and try incognito mode

### Service Startup Issues
1. Ensure setup service completes: `./run-legend.sh setup up`
2. Check MongoDB is healthy: `docker logs legend-mongodb`
3. Verify configuration files exist in `z_generated/`
4. Review service logs: `./run-legend.sh <profile> logs -f <service-name>`

### Clean Rebuild
```bash
# Remove all services and volumes
./run-legend.sh studio down -v

# Regenerate configurations
./run-legend.sh setup up

# Start services fresh
./run-legend.sh studio up -d
```

## NO CUSTOM CODE RULE

**ABSOLUTE RULE**: You are FORBIDDEN from creating custom code or configurations. You must ONLY use official open source solutions.

### What You CANNOT Do
- ❌ Write custom Dockerfiles
- ❌ Create custom docker-compose.yml files
- ❌ Modify existing configurations
- ❌ Create workarounds or "improvements"
- ❌ Write custom scripts beyond what exists

### What You MUST Do
- ✅ Use official FINOS Docker images
- ✅ Use official configuration templates
- ✅ Reference official documentation
- ✅ Point to official repositories
- ✅ Inform user if no official solution exists

## Documentation Rule

**ALWAYS UPDATE EXISTING DOCUMENTATION FILES** - Do not create new .md files unless absolutely necessary. Add new information to relevant existing files to keep the repository structure clean.

## References

Official FINOS Legend repositories:
- Engine: https://github.com/finos/legend-engine
- SDLC: https://github.com/finos/legend-sdlc
- Studio: https://github.com/finos/legend-studio
- Depot: https://github.com/finos/legend-depot

Docker Hub:
- https://hub.docker.com/u/finos

Official Deployment Tools:
- Docker Compose: https://github.com/finos/legend/tree/master/installers/docker-compose
- Helm Charts: https://github.com/finos/legend/tree/master/installers/helm-ocp