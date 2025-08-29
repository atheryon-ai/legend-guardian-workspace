# Local Development Setup

This directory contains Docker Compose configuration for running the Legend Guardian Agent with the full Legend stack locally.

## Quick Start

### 1. Set up environment variables

```bash
# Check if .env already exists
if [ ! -f .env ]; then
  # Copy the example environment file if it doesn't exist
  cp env.example .env
  echo "Created new .env file from env.example"
else
  echo ".env already exists, skipping creation"
fi

# Edit .env with your configuration
# At minimum, you may want to set:
# - API_KEY (for authentication)
# - PROJECT_ID and WORKSPACE_ID (for your Legend project)
```

### 2. Start the full Legend stack with agent

```bash
# Check for existing containers and clean up if needed
docker compose --profile full ps --quiet 2>/dev/null && \
  echo "Found existing containers, stopping them..." && \
  docker compose --profile full down

# Check if required images exist locally
echo "Checking for existing Docker images..."
for image in "finos/legend-engine-server:4.40.3" "finos/legend-sdlc-server:0.115.0" \
             "finos/legend-studio:8.38.0" "finos/legend-depot-server:1.5.3" \
             "mongo:4.2" "postgres:13"; do
  if docker image inspect "$image" >/dev/null 2>&1; then
    echo "✓ Found: $image"
  else
    echo "✗ Missing: $image (will be pulled)"
  fi
done

# Start all services (Legend Engine, SDLC, Studio, Depot, MongoDB, PostgreSQL, and Agent)
# Use --pull never if you want to use only local images
docker compose --profile full up -d

# Check status
docker compose --profile full ps

# View logs
docker compose --profile full logs -f
```

### 3. Access services

- **Legend Guardian Agent**: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/health
- **Legend Studio**: http://localhost:9000
- **Legend Engine**: http://localhost:6300
- **Legend SDLC**: http://localhost:6100
- **Legend Depot**: http://localhost:6200
- **MongoDB**: localhost:27017
- **PostgreSQL**: localhost:5432

## Available Profiles

### `default` profile
```bash
docker compose up -d
```
Starts core Legend services (Engine, SDLC, Studio, MongoDB) without the agent.

### `full` profile
```bash
docker compose --profile full up -d
```
Starts all services including:
- Legend Engine
- Legend SDLC  
- Legend Studio
- Legend Depot
- MongoDB
- PostgreSQL
- Legend Guardian Agent

## Development Workflow

### Start only the agent for development
```bash
# Check if Legend services are already running
if docker compose ps --services --filter "status=running" | grep -q "legend"; then
  echo "Legend services already running"
else
  echo "Starting Legend services..."
  docker compose up -d
fi

# Run agent in development mode (from project root)
make dev
```

### Stop services
```bash
# Check if services are running before stopping
if docker compose --profile full ps --quiet 2>/dev/null; then
  echo "Stopping running services..."
  docker compose --profile full down
else
  echo "No services running"
fi

# Stop and remove volumes (WARNING: this will delete data)
if docker compose --profile full ps --all --quiet 2>/dev/null; then
  echo "Removing containers and volumes..."
  docker compose --profile full down -v
fi
```

### View logs
```bash
# All services
docker compose --profile full logs -f

# Specific service
docker compose logs -f legend-guardian-agent
docker compose logs -f legend-engine
```

## Troubleshooting

### Service dependencies
The `full` profile includes proper service dependencies:
- Agent depends on Engine, SDLC, Depot, and Studio
- Studio depends on Engine and SDLC
- Engine and SDLC depend on MongoDB
- Depot depends on PostgreSQL

### Health checks
Services include health checks. If a service fails to start:
1. Check logs: `docker compose logs <service-name>`
2. Verify environment variables in `.env`
3. Ensure ports are not already in use

### Reset everything
```bash
# Stop and remove everything (if exists)
if docker compose --profile full ps --all --quiet 2>/dev/null; then
  echo "Cleaning up existing containers and volumes..."
  docker compose --profile full down -v
fi

# Optional: Remove Legend images (WARNING: will need to re-download)
echo "Legend images currently installed:"
docker images | grep -E "finos/legend|mongo|postgres" || echo "No Legend images found"
read -p "Remove Legend images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  docker images | grep "finos/legend" | awk '{print $3}' | xargs -r docker rmi
  echo "Legend images removed"
fi

# Start fresh
docker compose --profile full up -d
```

## Configuration

### Environment Variables
Key variables in `.env`:
- `API_KEY`: Authentication key for agent API
- `PROJECT_ID`: Your Legend project ID
- `WORKSPACE_ID`: Your Legend workspace ID
- Service URLs for external access

### Ports
Default ports (can be changed in docker-compose.yml):
- Agent: 8000
- Studio: 9000
- Engine: 6300
- SDLC: 6100
- Depot: 6200
- MongoDB: 27017
- PostgreSQL: 5432

## Next Steps

After starting the full profile:
1. Access the agent API at http://localhost:8000/docs
2. Test the health endpoint: http://localhost:8000/health
3. Run the test harness: `make harness` (from project root)
4. Explore individual use cases in `artifacts/harness/`
