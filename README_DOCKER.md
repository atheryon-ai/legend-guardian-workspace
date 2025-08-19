# Docker Setup for Legend Guardian Workspace

## 📁 Consolidated Structure

All Docker configurations have been consolidated for clarity:

```
legend-guardian-workspace/
├── Dockerfile                    # Guardian Agent application (Python)
├── docker-compose.yml           # Instructions pointing to deploy/local
└── deploy/
    └── local/
        ├── docker-compose.yml   # Complete Legend stack
        ├── start.sh             # Startup script
        └── config/              # Service configurations
            ├── engine-config.yml
            └── sdlc-config.yml
```

## 🚀 Quick Start

### Option 1: Run Everything (Recommended)
```bash
# From repository root
docker-compose -f deploy/local/docker-compose.yml --profile full up -d

# Or navigate to local directory
cd deploy/local
docker-compose --profile full up -d
```

### Option 2: Run Core Services Only
```bash
# Without Guardian Agent
docker-compose -f deploy/local/docker-compose.yml up -d
```

### Option 3: Use the helper script
```bash
cd deploy/local
./start.sh
```

## 🎯 Services & Ports

| Service | Container Name | Port | Health Check Endpoint |
|---------|---------------|------|----------------------|
| MongoDB | legend-mongodb | 27017 | N/A (internal) |
| Legend Engine | legend-engine | 6300 | /api/server/v1/info |
| Legend SDLC | legend-sdlc | 6100 | /api/info |
| Legend Studio | legend-studio | 9000 | / |
| Guardian Agent | legend-guardian | 8000 | /health |

## 🔧 Configuration

### Environment Variables
Create a `.env` file in `deploy/local/`:

```bash
# Legend versions
LEGEND_ENGINE_VERSION=4.40.3
LEGEND_SDLC_VERSION=0.195.0
LEGEND_STUDIO_VERSION=13.113.0

# GitLab OAuth (for SDLC)
GITLAB_HOST=gitlab.com
GITLAB_APP_ID=your-app-id
GITLAB_APP_SECRET=your-app-secret

# Guardian Agent
LEGEND_API_KEY=demo-key
VALID_API_KEYS=demo-key,test-key

# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=admin
MONGO_DATABASE=legend
```

### Service Profiles

The docker-compose uses profiles to control which services start:

- **Default** (no profile): MongoDB, Engine, SDLC, Studio
- **full** profile: All services including Guardian Agent

```bash
# Start with Guardian
docker-compose --profile full up -d

# Start without Guardian
docker-compose up -d
```

## 📊 Service Dependencies

```
MongoDB
  ├── Legend Engine
  │   └── Legend Studio
  └── Legend SDLC
      ├── Legend Studio
      └── Legend Guardian (monitors all)
```

## 🔍 Common Commands

### Check Status
```bash
# View all containers
docker-compose -f deploy/local/docker-compose.yml ps

# View logs
docker-compose -f deploy/local/docker-compose.yml logs -f [service-name]

# View specific service logs
docker-compose -f deploy/local/docker-compose.yml logs -f legend-engine
```

### Restart Services
```bash
# Restart all
docker-compose -f deploy/local/docker-compose.yml restart

# Restart specific service
docker-compose -f deploy/local/docker-compose.yml restart legend-studio
```

### Stop Services
```bash
# Stop all containers
docker-compose -f deploy/local/docker-compose.yml down

# Stop and remove volumes (clean slate)
docker-compose -f deploy/local/docker-compose.yml down -v
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using a port
lsof -i :6300

# Kill process using port
kill -9 $(lsof -t -i:6300)
```

### Container Won't Start
```bash
# Check logs
docker logs legend-engine

# Inspect container
docker inspect legend-engine

# Check resources
docker system df
docker stats
```

### Network Issues
```bash
# List networks
docker network ls

# Inspect network
docker network inspect legend-network

# Recreate network
docker-compose -f deploy/local/docker-compose.yml down
docker network rm legend-network
docker-compose -f deploy/local/docker-compose.yml up -d
```

### MongoDB Connection Issues
```bash
# Test MongoDB connection
docker exec -it legend-mongodb mongosh -u admin -p admin

# Check MongoDB logs
docker logs legend-mongodb
```

## 🏗️ Building Guardian Agent

The Guardian Agent is built from the root Dockerfile:

```bash
# Build manually
docker build -t legend-guardian:latest .

# Build via docker-compose
docker-compose -f deploy/local/docker-compose.yml build legend-guardian
```

## 🔄 Migration from Old Structure

If you were using the old docker-compose.yml in the root:

1. Stop old containers: `docker-compose down`
2. Remove old volumes if needed: `docker volume prune`
3. Use new location: `docker-compose -f deploy/local/docker-compose.yml up -d`

## 📝 Notes

- The root `Dockerfile` is for Guardian Agent only (Python application)
- All Legend services use official FINOS images from Docker Hub
- Custom Dockerfiles in `deploy/docker/` have been removed (redundant)
- Configuration is done via environment variables and mounted config files
- The consolidated setup ensures consistency across local and production environments