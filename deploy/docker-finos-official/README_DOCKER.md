# Docker Deployment for FINOS Legend (Full Stack)

This directory contains a comprehensive, profile-based Docker Compose setup for deploying a full FINOS Legend stack. This setup is highly configurable and allows you to run different combinations of services depending on your needs.

## Prerequisites

*   Docker and Docker Compose
*   GitLab OAuth credentials configured (see [GitLab OAuth Setup](../../GITLAB_OAUTH_SETUP.md))
*   Environment variables set in `.env.local` or `.env.docker` (see [Secrets Guide](../secrets/README.md))
*   The `run-legend.sh` script for proper deployment

## 1. Configuration

This deployment uses the **official FINOS Legend** configuration approach:

### Environment Variables
- **GitLab OAuth**: Set in `secrets.env` at the repository root
- **Service Configuration**: Configured in `deploy/docker/.env`
- **Secrets Management**: Use `secrets.example` as a template

### Required Setup
1. **Configure your environment**:
   ```bash
   # Run the interactive setup
   ../secrets/setup.sh --env docker --interactive
   ```

2. **Configure GitLab OAuth** in `.env.docker`:
   - `GITLAB_APP_ID`: Your GitLab OAuth application ID
   - `GITLAB_APP_SECRET`: Your GitLab OAuth application secret
   - `GITLAB_HOST`: GitLab instance (default: gitlab.com)

3. **Review docker-compose configuration** in `.env` (already configured)

## 2. First-Time Setup

Before launching the main services, you must run a one-time setup process. This will generate necessary configuration files based on your `.env` settings.

```bash
# From the repository root directory
docker-compose --profile setup -f deploy/docker/docker-compose.yml up --build
```

This command runs the `setup` service defined in the `docker-compose.yml`. The generated files will be placed in the `deploy/docker/z_generated` directory.

## 3. Running the Legend Services

You can launch different combinations of Legend services using Docker Compose profiles.

### Run the Core Stack (Studio, SDLC, Engine)

This profile brings up the essential services for data modeling.

```bash
# From the repository root directory
docker-compose --profile studio -f deploy/docker/docker-compose.yml up -d --build
```

### Run the Full Stack (including Depot and Query)

This profile launches all services, including `legend-depot` for sharing and `legend-query` for data exploration.

```bash
# From the repository root directory
docker-compose --profile query -f deploy/docker/docker-compose.yml up -d --build
```

### Available Profiles

*   `setup`: (One-time) Generates configurations.
*   `engine`: Runs the Legend Engine.
*   `sdlc`: Runs the Legend SDLC server.
*   `studio`: Runs the core modeling stack (Studio, SDLC, Engine, MongoDB).
*   `depot`: Runs the `legend-depot` services for model sharing.
*   `query`: Runs the full stack, including `legend-query`.
*   `postgres`: Includes a PostgreSQL instance (used by some services).

## 4. Service Management

### Check Status

```bash
# From the repository root directory
docker-compose -f deploy/docker/docker-compose.yml ps
```

### View Logs

```bash
# View all logs
docker-compose -f deploy/docker/docker-compose.yml logs -f

# View logs for a specific service
docker-compose -f deploy/docker/docker-compose.yml logs -f legend-studio
```

### Stop Services

```bash
# Stop and remove containers
docker-compose -f deploy/docker/docker-compose.yml down

# Stop and remove containers and volumes (deletes all data)
docker-compose -f deploy/docker/docker-compose.yml down -v
```

## 5. Services and Ports

The following services are included. Ports and other settings are configured in your `.env` file.

| Service | Container Name | Default Port | Profile(s) | Description |
|---|---|---|---|---|
| Legend Studio | `legend-studio` | `${STUDIO_PORT}` | `studio`, `query` | Web-based data modeling UI. |
| Legend SDLC | `legend-sdlc` | `${SDLC_PORT}` | `sdlc`, `studio`, `query` | Source code and lifecycle management. |
| Legend Engine | `legend-engine` | `${ENGINE_PORT}` | `engine`, `studio`, `query` | Model execution engine. |
| Legend Depot | `legend-depot` | `${DEPOT_PORT}` | `depot`, `query` | Service for storing and sharing data models. |
| Legend Query | `legend-query` | `${QUERY_PORT}` | `query` | UI for exploring and querying data. |
| MongoDB | `legend-mongodb` | `${MONGODB_PORT}` | `engine`, `sdlc`, etc. | Primary database for Legend services. |
| PostgreSQL | `postgres` | `5432` | `postgres`, `studio`, `query` | Relational database for specific services. |

## 6. Current Deployment Status

### ✅ **Successfully Deployed**
This deployment is now using the **official FINOS Legend** approach with:
- **Official docker-compose.yml** - Complete service orchestration
- **Official setup.sh** - Configuration generation working
- **GitLab OAuth integration** - Using secrets.env for credentials
- **Profile-based deployment** - Flexible service combinations
- **Production-ready configuration** - Health checks, proper dependencies

### 🚀 **Deployment Commands**
```bash
# One-time setup (generates configurations)
./run-legend.sh setup up

# Core Legend Studio stack
./run-legend.sh studio up -d

# Full Legend stack with Query
./run-legend.sh query up -d

# Individual services
./run-legend.sh engine up -d
./run-legend.sh sdlc up -d
./run-legend.sh depot up -d
```

### 🔍 **Service Management**
```bash
# Check status
./run-legend.sh studio ps

# View logs
./run-legend.sh studio logs -f

# Stop services
./run-legend.sh studio down
```

### 🌐 **Access URLs**
- **Legend Studio**: http://localhost:9000/studio
- **Legend SDLC**: http://localhost:6100
- **Legend Engine**: http://localhost:6300
- **Legend Depot**: http://localhost:6200
- **Legend Query**: http://localhost:9001/query
- **MongoDB**: localhost:27017
- **PostgreSQL**: localhost:5432

## 7. Troubleshooting

### Common Issues
1. **GitLab OAuth errors**: Ensure .env.docker is properly configured
2. **Service startup failures**: Check that setup service completed successfully
3. **Port conflicts**: Verify ports are available in your environment
4. **Configuration issues**: Run setup service again to regenerate configs

### Getting Help
- Check service logs: `./run-legend.sh studio logs -f`
- Verify environment variables: `./run-legend.sh studio config`
- Review official FINOS documentation: [FINOS Legend](https://github.com/finos/legend)