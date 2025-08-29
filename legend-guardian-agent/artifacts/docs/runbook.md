# Legend Guardian Agent - Operations Runbook

## Quick Start

### Local Development

1. **Clone and Setup**
```bash
git clone <repository>
cd legend-guardian-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp deploy/local/.env.example .env
# Edit .env with your configuration
```

3. **Start Services**
```bash
# Using Docker Compose
docker compose --profile full up -d

# Or run agent locally
make dev
```

4. **Verify Health**
```bash
curl http://localhost:8000/health | jq '.'
```

## Service URLs

| Service | URL | Health Check |
|---------|-----|--------------|
| Agent | http://localhost:8000 | `/health` |
| Engine | http://localhost:6300 | `/api/server/v1/info` |
| SDLC | http://localhost:6100 | `/api/info` |
| Depot | http://localhost:6200 | `/api/info` |
| Studio | http://localhost:9000 | `/studio` |

## Common Operations

### Check Service Status

```bash
# All services
make health

# Individual service
curl http://localhost:8000/health | jq '.services.engine'
```

### View Logs

```bash
# Docker logs
docker compose logs -f agent

# Local development
tail -f logs/agent.log
```

### Run Tests

```bash
# All tests
make test

# Specific use case
bash artifacts/harness/usecase1_ingest_publish.sh
```

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f deploy/k8s/

# Check deployment
kubectl get pods -n legend-guardian
kubectl logs -f deployment/legend-guardian-agent -n legend-guardian
```

## Troubleshooting

### Agent Not Starting

**Symptom**: Agent fails to start or crashes immediately

**Checks**:
1. Verify all environment variables are set
2. Check Legend services are running
3. Review logs for connection errors

**Solution**:
```bash
# Check environment
env | grep -E "ENGINE_URL|SDLC_URL|DEPOT_URL"

# Test connectivity
curl http://localhost:6300/api/server/v1/info
curl http://localhost:6100/api/info

# Restart services
docker compose restart
```

### Compilation Failures

**Symptom**: PURE code fails to compile

**Checks**:
1. Verify PURE syntax
2. Check for missing dependencies
3. Review compilation errors

**Solution**:
```bash
# Test compilation directly
curl -X POST http://localhost:8000/adapters/engine/compile \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{"pure": "Class model::Test {}"}'
```

### Service Not Accessible

**Symptom**: Generated services return 404

**Checks**:
1. Verify service was deployed
2. Check service path
3. Review Engine logs

**Solution**:
```bash
# List services
curl http://localhost:6300/api/services

# Test service directly
curl http://localhost:6300/api/service/trades/byNotional
```

### Database Connection Issues

**Symptom**: Database connection errors in logs

**Checks**:
1. Verify database is running
2. Check connection strings
3. Test connectivity

**Solution**:
```bash
# MongoDB
docker exec -it legend-mongodb mongosh --eval "db.adminCommand('ping')"

# PostgreSQL
docker exec -it legend-postgres psql -U legend -c "SELECT 1"
```

### Authentication Failures

**Symptom**: 401 Unauthorized errors

**Checks**:
1. Verify API key is correct
2. Check token format
3. Review auth configuration

**Solution**:
```bash
# Test with correct header
curl -H "Authorization: Bearer demo-key" \
  http://localhost:8000/health
```

## Performance Tuning

### Agent Configuration

```yaml
# Adjust in .env or ConfigMap
REQUEST_TIMEOUT: 60  # Increase for slow operations
MAX_RETRIES: 5       # More retries for unstable networks
AGENT_MAX_TOKENS: 4000  # Increase for complex operations
```

### Resource Limits

```yaml
# Kubernetes resources
resources:
  requests:
    memory: "1Gi"    # Increase for large models
    cpu: "500m"      # Increase for faster processing
  limits:
    memory: "2Gi"
    cpu: "2"
```

### Connection Pooling

```python
# In settings.py
POOL_SIZE = 20  # Increase for high concurrency
POOL_TIMEOUT = 30
```

## Monitoring

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Key metrics to watch:
- request_duration_seconds
- request_count_total
- error_count_total
- active_connections
```

### Alerts

Configure alerts for:
- Service health down > 5 minutes
- Error rate > 5%
- Response time > 2 seconds
- Memory usage > 80%

### Dashboards

Import Grafana dashboards from:
```
deploy/local/config/grafana-dashboards/
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup database
docker exec legend-mongodb mongodump --out /backup/

# Backup configurations
tar -czf config-backup.tar.gz deploy/local/config/
```

### Restore Procedure

```bash
# Restore database
docker exec legend-mongodb mongorestore /backup/

# Restore configurations
tar -xzf config-backup.tar.gz
```

## Security

### Rotate API Keys

1. Generate new keys
2. Update `.env` or secrets
3. Restart services
4. Test with new keys
5. Revoke old keys

### Update Dependencies

```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Audit Logs

```bash
# View security events
grep "AUTH\|SECURITY" logs/agent.log

# Export for analysis
docker logs legend-guardian-agent 2>&1 | grep -E "401|403" > auth-failures.log
```

## Incident Response

### Immediate Actions

1. **Identify Impact**
   - Check health endpoints
   - Review error logs
   - Monitor metrics

2. **Isolate Problem**
   - Identify failing component
   - Check recent changes
   - Review dependencies

3. **Mitigate**
   - Rollback if needed
   - Scale resources
   - Implement workaround

### Rollback Procedure

```bash
# Kubernetes rollback
kubectl rollout undo deployment/legend-guardian-agent -n legend-guardian

# Docker rollback
docker compose down
git checkout <last-known-good>
docker compose up -d
```

## Contact Information

- **On-call**: DevOps Team
- **Escalation**: Platform Team Lead
- **Legend Support**: legend@finos.org
- **Repository**: [GitHub Issues]

## Appendix

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| ENGINE_URL | Legend Engine URL | http://localhost:6300 |
| SDLC_URL | Legend SDLC URL | http://localhost:6100 |
| DEPOT_URL | Legend Depot URL | http://localhost:6200 |
| API_KEY | API authentication key | demo-key |
| LOG_LEVEL | Logging level | INFO |
| OTEL_ENABLED | Enable OpenTelemetry | false |

### Port Reference

| Port | Service | Protocol |
|------|---------|----------|
| 8000 | Agent API | HTTP |
| 6300 | Engine | HTTP |
| 6100 | SDLC | HTTP |
| 6200 | Depot | HTTP |
| 9000 | Studio | HTTP |
| 27017 | MongoDB | TCP |
| 5432 | PostgreSQL | TCP |