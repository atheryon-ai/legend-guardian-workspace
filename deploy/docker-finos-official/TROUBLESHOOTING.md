# Legend Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. "Unauthorized" Error Banner in Legend Studio

**Problem**: A red "Unauthorized" banner appears at the bottom of Legend Studio UI even after successful GitLab authentication.

**Root Cause**: 
- Session serialization version mismatch between Legend services
- Corrupted session data in MongoDB from previous deployments
- Services not sharing authentication context properly

**Solution**:
```bash
# Step 1: Stop and remove all Legend containers
docker ps -a | grep legend | awk '{print $1}' | xargs docker rm -f

# Step 2: Ensure .env.local is in the repository root
# The file should be at: legend-guardian-workspace/.env.local
# NOT at: legend-guardian-workspace/deploy/docker-finos-official/.env.local
mv deploy/docker-finos-official/.env.local .env.local  # if needed

# Step 3: Verify GitLab credentials are set
cat .env.local | grep GITLAB_APP

# Step 4: Regenerate configurations and restart
cd deploy/docker-finos-official
./run-legend.sh setup up
./run-legend.sh studio up -d

# Step 5: Clear browser cache for localhost
# Chrome/Edge: F12 → Application → Storage → Clear site data
# Or use Incognito/Private browsing mode

# Step 6: Access Legend Studio
# Navigate to: http://localhost:9000/studio
# Complete GitLab OAuth login when prompted
```

### 2. Services Not Starting - Container Name Conflicts

**Problem**: Error message "The container name is already in use"

**Solution**:
```bash
# Remove all Legend-related containers
docker ps -a | grep -E "legend|setup|postgres" | awk '{print $1}' | xargs docker rm -f

# Restart with clean state
./run-legend.sh setup up
./run-legend.sh studio up -d
```

### 3. GitLab OAuth Configuration Issues

**Problem**: Authentication redirects fail or OAuth errors occur

**Checklist**:
1. **GitLab App Configuration**:
   - App must be marked as "Confidential"
   - Redirect URI: `http://localhost:6100/api/auth/callback`
   - Scopes: `api`, `read_user`, `openid`, `profile`

2. **Local Configuration**:
   ```bash
   # Verify .env.local exists in repo root
   ls -la ~/.../legend-guardian-workspace/.env.local
   
   # Check credentials are set
   grep GITLAB .env.local
   ```

3. **Test OAuth Endpoint**:
   ```bash
   curl -I https://gitlab.com/.well-known/openid-configuration
   # Should return HTTP/2 200
   ```

### 4. MongoDB Connection Issues

**Problem**: Services can't connect to MongoDB

**Solution**:
```bash
# Check MongoDB is running
docker ps | grep mongodb

# Check MongoDB logs
docker logs legend-mongodb --tail 50

# Verify MongoDB credentials in .env.local
grep MONGODB .env.local
# Should show: MONGODB_URI=mongodb://admin:password@legend-mongodb:27017
```

### 5. CORS Errors in Browser Console

**Problem**: Cross-Origin Resource Sharing errors when Studio calls SDLC API

**Verification**:
```bash
# Test CORS headers
curl -I -H "Origin: http://localhost:9000" http://localhost:6100/api/info
# Should include: Access-Control-Allow-Origin: http://localhost:9000
```

**Solution**: Restart services to ensure proper CORS configuration is loaded.

### 6. Service Health Check Failures

**Problem**: Services show as unhealthy in Docker

**Debug Steps**:
```bash
# Check service status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific service logs
docker logs legend-sdlc --tail 100
docker logs legend-engine --tail 100
docker logs legend-studio --tail 100

# Test service endpoints
curl http://localhost:6100/api/info     # SDLC
curl http://localhost:6300/api/server/v1/info  # Engine
curl http://localhost:9000/studio       # Studio
```

### 7. Environment Variables Not Loading

**Problem**: Services start but GitLab authentication fails

**Solution**:
```bash
# Verify environment variables are loaded in containers
docker exec legend-sdlc sh -c 'echo $GITLAB_APP_ID' | head -c 20
docker exec legend-studio sh -c 'echo $GITLAB_APP_ID' | head -c 20

# If empty, ensure .env.local is in correct location
# Must be at repository root, not in deploy/docker-finos-official/
```

## Quick Diagnostic Commands

```bash
# Check all Legend services status
docker ps | grep legend

# View recent logs for all Legend services
for service in legend-studio legend-sdlc legend-engine legend-mongodb; do
  echo "=== $service ==="
  docker logs $service --tail 10 2>&1 | grep -E "ERROR|WARN|Exception"
done

# Test all service endpoints
curl -s http://localhost:6100/api/info | jq .
curl -s http://localhost:6300/api/server/v1/info | jq .
curl -s http://localhost:9000/studio/version.json | jq .

# Check Docker resource usage
docker stats --no-stream | grep legend
```

## Complete Reset Procedure

If all else fails, perform a complete reset:

```bash
# 1. Stop everything
cd deploy/docker-finos-official
docker-compose down -v

# 2. Remove all containers and volumes
docker ps -a | grep legend | awk '{print $1}' | xargs docker rm -f
docker volume ls | grep legend | awk '{print $2}' | xargs docker volume rm

# 3. Clear generated configurations
rm -rf z_generated/

# 4. Ensure .env.local is properly configured
cp .env.example ../../.env.local
# Edit ../../.env.local with your GitLab credentials

# 5. Rebuild from scratch
./run-legend.sh setup up
./run-legend.sh studio up -d

# 6. Clear browser cache and cookies for localhost

# 7. Access Legend Studio fresh
open http://localhost:9000/studio
```

## Getting Help

If issues persist:
1. Check service logs for specific error messages
2. Ensure you're using official FINOS Docker images
3. Verify your system meets minimum requirements (Docker, memory, ports)
4. Report issues at: https://github.com/finos/legend/issues