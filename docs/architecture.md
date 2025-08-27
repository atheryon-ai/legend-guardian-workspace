# Atheryon FINOS Legend - System Architecture

## Overview

This project provides a clean, focused deployment of the FINOS Legend platform using Docker. The architecture is designed to be simple, maintainable, and focused solely on Legend platform deployment.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Atheryon FINOS Legend                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Legend       │  │   Legend        │  │   Legend        │ │
│  │   Engine       │  │   SDLC          │  │   Studio        │ │
│  │  (Port 6300)   │  │  (Port 6100)    │  │  (Port 9000)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    MongoDB                             │ │
│  │                   (Port 27017)                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Service Dependencies

```
MongoDB (27017)
  ├── Legend Engine (6300)
  │   └── Legend Studio (9000)
  └── Legend SDLC (6100)
      ├── Legend Studio (9000)
      └── Legend Engine (6300)
```

## 🐳 Docker Architecture

### Container Structure

```
deploy/docker/
├── components/           # Legend service components
│   ├── engine/          # Legend Engine
│   │   └── Dockerfile.engine
│   ├── sdlc/            # Legend SDLC  
│   │   └── Dockerfile.sdlc
│   └── studio/          # Legend Studio
│       └── Dockerfile.studio
├── config/              # Configuration files
│   ├── engine-config.yml
│   └── sdlc-config.yml
└── docker-compose.yml   # Main deployment file
```

### Network Architecture

- **Network**: `legend-network` (bridge)
- **Internal Communication**: Services communicate via container names
- **External Access**: Ports exposed to host machine
- **Data Persistence**: MongoDB data persisted via Docker volumes

## 🔧 Configuration Architecture

### Configuration Files

- **Engine Config** (`engine-config.yml`): Legend Engine settings
- **SDLC Config** (`sdlc-config.yml`): Legend SDLC settings

### Environment Variables

- **Service Ports**: Configured in docker-compose.yml
- **Database URLs**: MongoDB connection strings
- **Service Dependencies**: Internal service URLs

## 📊 Health Monitoring

### Health Check Endpoints

- **Legend Engine**: `/api/server/v1/info`
- **Legend SDLC**: `/api/health`
- **Legend Studio**: `/` (root endpoint)

### Health Check Configuration

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:6300/api/server/v1/info"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🚀 Deployment Architecture

### Single Command Deployment

```bash
cd deploy/docker
docker-compose up -d
```

### Service Startup Order

1. **MongoDB** - Database backend
2. **Legend Engine** - Model execution engine
3. **Legend SDLC** - Source control (depends on Engine)
4. **Legend Studio** - Web interface (depends on Engine & SDLC)

## 🔒 Security Architecture

### Network Security

- **Internal Network**: Services communicate via Docker network
- **Port Exposure**: Only necessary ports exposed to host
- **No External Access**: Services not accessible from internet by default

### Data Security

- **MongoDB**: No authentication by default (development setup)
- **Service Communication**: Internal network communication only
- **Configuration**: Mounted from host filesystem

## 📈 Scalability Considerations

### Current Design

- **Single Instance**: Each service runs as single container
- **Resource Limits**: No explicit resource constraints
- **Horizontal Scaling**: Not implemented in current design

### Future Enhancements

- **Load Balancing**: Add reverse proxy (nginx/traefik)
- **Resource Limits**: Implement Docker resource constraints
- **Horizontal Scaling**: Multiple instances of services
- **Persistent Storage**: External volume mounts for production

## 🛠️ Maintenance Architecture

### Logging

- **Container Logs**: Accessible via `docker-compose logs`
- **Log Rotation**: Managed by Docker daemon
- **Centralized Logging**: Not implemented (future enhancement)

### Monitoring

- **Health Checks**: Built-in Docker health checks
- **Metrics Collection**: Not implemented (future enhancement)
- **Alerting**: Not implemented (future enhancement)

### Backup & Recovery

- **MongoDB Data**: Persisted in Docker volumes
- **Configuration**: Stored in version control
- **Backup Strategy**: Manual volume backup (future enhancement)

## 🔄 Update & Deployment

### Service Updates

```bash
# Rebuild and restart specific service
docker-compose build legend-engine
docker-compose up -d legend-engine

# Update all services
docker-compose down
docker-compose build
docker-compose up -d
```

### Configuration Updates

- **Runtime Updates**: Not supported (requires restart)
- **Configuration Changes**: Modify config files and restart services
- **Version Management**: Docker image versioning

## 📋 Architecture Decisions

### Why Docker Compose?

- **Simplicity**: Single file deployment
- **Development**: Easy local development and testing
- **Consistency**: Same environment across development/production
- **Maintenance**: Simple service management

### Why Official FINOS Images?

- **Reliability**: Official, tested images
- **Updates**: Regular security and feature updates
- **Compatibility**: Guaranteed compatibility with Legend platform
- **Support**: Official support from FINOS

### Why MongoDB?

- **Legend Requirement**: Legend platform requires MongoDB
- **Simplicity**: No complex database setup
- **Performance**: Adequate for development and small deployments
- **Future**: Can be replaced with external MongoDB in production

## 🎯 What This Architecture Does NOT Include

- ❌ **Guardian Agent**: No monitoring or automation
- ❌ **Load Balancing**: No reverse proxy or load balancer
- ❌ **High Availability**: No clustering or failover
- ❌ **External Monitoring**: No Prometheus, Grafana, etc.
- ❌ **CI/CD Pipeline**: No automated deployment
- ❌ **Production Hardening**: No security hardening or resource limits

This architecture is designed for **development, testing, and small production deployments** of the Legend platform.
