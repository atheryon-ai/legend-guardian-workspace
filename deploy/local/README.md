# Local Development Environment

This directory contains everything needed to run the Legend platform locally using Docker Compose.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 8GB RAM allocated to Docker
- Ports 6100, 6300, 9000, and 27017 available

### 1. Setup Environment

```bash
# If you do not already have a secrets.env file, copy the example:
if [ ! -f ../secrets.env ]; then
  cp ../secrets.example ../secrets.env
fi
# Then edit secrets.env with your GitLab OAuth credentials and other secrets (required):
nano ../secrets.env
```

### 2. Start Services

```bash
# Start all Legend services
docker-compose up -d

# Or start without Guardian Agent
docker-compose up -d legend-engine legend-sdlc legend-studio

# To include Guardian Agent (if using profiles)
docker-compose --profile guardian up -d
```

### 3. Access Services

Once running, access the services at:

- **Legend Studio**: http://localhost:9000
- **Legend Engine**: http://localhost:6300
- **Legend SDLC**: http://localhost:6100
- **MongoDB**: mongodb://localhost:27017
- **Guardian Agent**: http://localhost:8000 (if enabled)

## 📁 Directory Structure

```
local/
├── docker-compose.yml    # Main compose file
├── ../secrets.example   # Secrets template (one level up)
├── ../secrets.env       # Your secrets (git-ignored, one level up)
├── .env.example         # (optional) local environment template
├── .env                 # (optional) local environment (git-ignored)
├── config/              # Service configurations
│   ├── engine-config.yml
│   └── sdlc-config.yml
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables & Secrets

The `../secrets.env` file controls:
- GitLab OAuth credentials
- Azure credentials
- API keys
- Domain names

This file is loaded into your containers using the `env_file` directive in `docker-compose.yml`.

If you need a local .env file for Docker Compose overrides or local development, only copy .env.example to .env if .env does not already exist:
```bash
if [ ! -f .env ]; then
  cp .env.example .env
fi
```
Then edit .env as needed.

### Service Configurations

Configuration files in `config/` directory:
- `engine-config.yml` - Legend Engine settings
- `sdlc-config.yml` - Legend SDLC settings

These are mounted as volumes into the containers.

## 🛠️ Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f legend-studio
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart legend-engine
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean start)
docker-compose down -v
```

### Update Images

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d
```

## 🔍 Troubleshooting

### Service Won't Start

1. Check port availability:
```bash
lsof -i :6300  # Check if port is in use
```

2. Check logs:
```bash
docker-compose logs legend-engine
```

3. Verify Docker resources:
```bash
docker system df
docker stats
```

### MongoDB Connection Issues

If services can't connect to MongoDB:

1. Ensure MongoDB is healthy:
```bash
docker-compose ps mongodb
docker-compose logs mongodb
```

2. Test connection:
```bash
docker exec -it legend-mongodb mongosh -u admin -p admin
```

### Studio Can't Connect to Backend

1. Check backend services are running:
```bash
curl http://localhost:6300/api/server/v1/info
curl http://localhost:6100/api/info
```

2. Verify environment variables in Studio:
```bash
docker-compose exec legend-studio env | grep LEGEND
```

## 🧪 Testing the Setup

### 1. Test Legend Engine

```bash
curl http://localhost:6300/api/server/v1/info
```

Expected: JSON with server information

### 2. Test Legend SDLC

```bash
curl http://localhost:6100/api/info
```

Expected: JSON with SDLC information

### 3. Test Legend Studio

Open http://localhost:9000 in your browser. You should see the Legend Studio interface.

### 4. Test Guardian Agent (if enabled)

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy"}`

## 🔄 Development Workflow

### 1. Making Configuration Changes

1. Edit configuration files in `config/`
2. Restart affected service:
```bash
docker-compose restart legend-engine
```

### 2. Testing with Guardian Agent

```bash
# Start with Guardian profile
docker-compose --profile guardian up -d

# Send test event
curl -X POST http://localhost:8000/api/v1/model/change \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"TestModel","change":"update"}'
```

### 3. Connecting to External GitLab

1. Create GitLab OAuth App:
   - Go to https://gitlab.com/-/profile/applications
   - Name: "Legend Local Dev"
   - Redirect URI: `http://localhost:6100/api/auth/callback`
   - Scopes: `api`, `read_user`, `openid`

2. Update `../secrets.env` with credentials:
```bash
GITLAB_APP_ID=your-app-id
GITLAB_APP_SECRET=your-app-secret
```

3. Restart SDLC service:
```bash
docker-compose restart legend-sdlc
```

## 🚧 Advanced Configuration

### Custom MongoDB Setup

To use an external MongoDB:

1. Update `.env`:
```bash
MONGODB_URI=mongodb://user:pass@host:port/database
```

2. Remove MongoDB service from compose:
```bash
docker-compose up -d legend-engine legend-sdlc legend-studio
```

### Resource Limits

Add resource limits to services in `docker-compose.yml`:

```yaml
services:
  legend-engine:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Network Isolation

For production-like isolation, use separate networks:

```yaml
networks:
  frontend:
  backend:
  database:
```

## 📚 Additional Resources

- [Legend Documentation](https://legend.finos.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Documentation](https://docs.mongodb.com/)

## 🤝 Contributing

When making changes to the local development setup:

1. Test all services start correctly
2. Update this README with any new steps
3. Keep `../secrets.example` in sync with required variables
4. Test both with and without Guardian Agent profile