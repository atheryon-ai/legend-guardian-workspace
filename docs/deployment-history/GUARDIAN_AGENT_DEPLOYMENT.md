# Legend Guardian Agent - Azure AKS Deployment Guide

## 🚀 **Deploy to Azure AKS**

Your Legend Guardian Agent is designed to run on Azure AKS alongside your existing Legend services, not locally.

## 📋 **Prerequisites**

- ✅ Azure CLI installed and logged in
- ✅ kubectl installed and configured
- ✅ Docker running locally
- ✅ Access to Azure Container Registry (ACR)
- ✅ Access to Azure Kubernetes Service (AKS)

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure AKS Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Legend        │  │   Legend        │  │   Legend        │ │
│  │   Engine        │  │   SDLC          │  │   Studio        │ │
│  │  (Port 6060)    │  │  (Port 7070)    │  │  (Port 9000)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                    │                    │         │
│           └────────────────────┼────────────────────┘         │
│                                │                              │
│                                ▼                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Legend Guardian Agent                        │ │
│  │                   (Port 8000)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Deployment**

### **Step 1: Generate API Keys (Required First)**

```bash
# Navigate to azure-deployment directory
cd azure-deployment

# Generate and encode API keys
./generate-api-keys.sh
```

This will:
- Prompt you for your Legend Platform API key
- Generate external API keys for the Guardian Agent
- Create the Kubernetes secrets file
- Create a local .env file for development

### **Step 2: Deploy to Azure AKS**

```bash
# Deploy the Guardian Agent
./deploy-guardian-agent.sh
```

### **Option 2: Manual Deployment**

```bash
# 1. Build Docker image
docker build -t legend-guardian-agent:latest .

# 2. Tag for ACR
docker tag legend-guardian-agent:latest <acr-name>.azurecr.io/legend-guardian-agent:latest

# 3. Push to ACR
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/legend-guardian-agent:latest

# 4. Deploy to Kubernetes
kubectl apply -f azure-deployment/k8s/legend-guardian-agent.yaml
```

## 🔧 **Configuration**

### **Environment Variables**

The agent is configured to connect to your Azure Legend services:

```yaml
env:
  - name: LEGEND_ENGINE_URL
    value: "http://legend-engine:6060"  # Internal K8s service
  - name: LEGEND_SDLC_URL
    value: "http://legend-sdlc:7070"    # Internal K8s service
  - name: LEGEND_API_KEY
    valueFrom:
      secretKeyRef:
        name: legend-secrets
        key: api-key
```

### **Service Discovery**

- **Legend Engine**: `http://legend-engine:6060` (internal K8s service)
- **Legend SDLC**: `http://legend-sdlc:7070` (internal K8s service)
- **Legend Guardian Agent**: `http://legend-guardian-agent:8000` (internal K8s service)

## 🌐 **Access Methods**

### **1. Port Forward (Development/Testing)**

```bash
# Forward agent service to local machine
kubectl port-forward -n legend svc/legend-guardian-agent 8000:8000

# Test locally
curl http://localhost:8000/health
```

### **2. Ingress (Production)**

The agent is accessible via:
- **URL**: `http://guardian.52.186.106.13.nip.io`
- **Health Check**: `http://guardian.52.186.106.13.nip.io/health`
- **API Docs**: `http://guardian.52.186.106.13.nip.io/docs`

### **3. Internal Service (Within Cluster)**

```bash
# From another pod in the cluster
curl http://legend-guardian-agent:8000/health
```

## 📊 **Monitoring & Health**

### **Health Checks**

- **Liveness Probe**: `/health` endpoint every 10 seconds
- **Readiness Probe**: `/health` endpoint every 5 seconds
- **Startup Delay**: 30 seconds for liveness, 5 seconds for readiness

### **Resource Limits**

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

## 🔍 **Troubleshooting**

### **Check Deployment Status**

```bash
# Check pods
kubectl get pods -n legend -l app=legend-guardian-agent

# Check logs
kubectl logs -n legend -l app=legend-guardian-agent

# Check service
kubectl get svc -n legend legend-guardian-agent

# Check ingress
kubectl get ingress -n legend legend-guardian-agent-ingress
```

### **Common Issues**

1. **Image Pull Error**: Ensure ACR credentials are correct
2. **Service Unavailable**: Check if Legend Engine/SDLC are running
3. **Connection Refused**: Verify internal service names and ports

### **Debug Mode**

Enable debug logging by setting:
```yaml
env:
  - name: LEGEND_API_DEBUG
    value: "true"
  - name: LEGEND_LOG_LEVEL
    value: "DEBUG"
```

## 🚀 **Next Steps**

After successful deployment:

1. **Test the Agent**: Use the health check endpoint
2. **Send Model Changes**: Test the `/api/v1/model/change` endpoint
3. **Monitor Logs**: Watch agent activity in real-time
4. **Scale if Needed**: Adjust replica count based on load

## 📚 **API Endpoints**

Once deployed, your agent provides:

- `GET /health` - Health check
- `GET /` - Service information
- `POST /api/v1/model/change` - Handle model changes
- `POST /api/v1/model/validate` - Validate models
- `GET /api/v1/system/status` - System status
- `GET /api/v1/memory/events` - Event history
- `GET /docs` - Interactive API documentation

---

**🎉 Your Legend Guardian Agent is now running on Azure AKS and ready to monitor your Legend platform!**
