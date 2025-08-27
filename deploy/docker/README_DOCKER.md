# Docker Deployment for FINOS Legend (Full Stack)

This directory contains a comprehensive, profile-based Docker Compose setup for deploying a full FINOS Legend stack. This setup is highly configurable and allows you to run different combinations of services depending on your needs.

## Prerequisites

*   Docker and Docker Compose
*   A `.env` file for configuration.

## 1. Configuration

This deployment is configured using a `.env` file located in this directory (`deploy/docker/.env`).

If you do not have one, you can copy the example configuration file:

```bash
cp .env.example .env
```

After creating the file, **review and edit the variables in `.env`**, especially for GitLab integration and any secret keys, to match your environment.

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