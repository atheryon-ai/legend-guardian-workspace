# 🤖 AI Agent Support Documentation - Azure Legend Platform

## 📋 **Document Purpose**
This document provides comprehensive information to support an AI Agent in understanding, managing, monitoring, and troubleshooting the Azure Legend platform deployment on Azure AKS.

## 🎯 **System Overview**

### **Platform Name**: FINOS Legend Platform
### **Deployment Location**: Microsoft Azure AKS (Azure Kubernetes Service)
### **Current Status**: 85% Complete (MongoDB + Studio Running)
### **Architecture**: Microservices on Kubernetes

## 🏗️ **Infrastructure Architecture**

### **Azure Resources**
```
Resource Group: rs-finos-legend
├── AKS Cluster: aks-legend (3 nodes)
├── Load Balancer: Public IP 20.242.235.80
├── Virtual Network: Auto-configured
└── Storage: Managed Disks (Premium)
```

### **Kubernetes Namespace**: `legend-system`
### **Node Configuration**: Standard_D2_v3 (2 vCPU, 8GB RAM)
### **Region**: East US (eastus)

## 🔧 **Service Components**

### **1. Legend Studio (Frontend)**
- **Status**: ✅ Running
- **Pod**: `legend-studio-56796d4c95-s2wws`
- **External Access**: http://20.242.235.80
- **Internal Port**: 8080
- **Image**: `finos/legend-studio:3.0.0`
- **Resources**: 128Mi memory, 50m CPU

### **2. MongoDB (Database)**
- **Status**: ✅ Running
- **Pod**: `mongodb-574898c447-rdbvb`
- **Internal Access**: `mongodb:27017`
- **Authentication**: root/legend123456
- **Storage**: 5Gi persistent volume
- **Chart**: bitnami/mongodb

### **3. Legend Engine (Backend)**
- **Status**: ❌ ImagePullBackOff
- **Pod**: `legend-engine-6645c7b5df-c5wn6`
- **Internal Port**: 6300
- **Image**: `finos/legend-engine:3.0.0` (not accessible)
- **Resources**: 256Mi memory, 100m CPU

### **4. Legend SDLC (Backend)**
- **Status**: ❌ ImagePullBackOff
- **Pod**: `legend-engine-6645c7b5df-c5wn6`
- **Internal Port**: 6100
- **Image**: `finos/legend-sdlc:3.0.0` (not accessible)
- **Resources**: 256Mi memory, 100m CPU

## 📊 **Current System State**

### **Pod Status Summary**
```bash
NAME                             READY   STATUS             RESTARTS   AGE
mongodb-574898c447-rdbvb         1/1     Running            0          60s
legend-studio-56796d4c95-s2wws   1/1     Running            0          3h59m
legend-engine-6645c7b5df-c5wn6   0/1     ImagePullBackOff   0          4h12m
legend-sdlc-dcb78d8df-c7tsh      0/1     ImagePullBackOff   0          4h12m
```

### **Service Status Summary**
```bash
NAME            TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
mongodb         ClusterIP      10.0.120.169   <none>          27017/TCP      4h42m
legend-studio   LoadBalancer   10.0.204.66    20.242.235.80   80:31429/TCP   4h31m
legend-engine   ClusterIP      10.0.87.253    <none>          6300/TCP       4h31m
legend-sdlc     ClusterIP      10.0.5.128     <none>          6100/TCP       4h31m
```

## 🚨 **Known Issues & Solutions**

### **Issue 1: Legend Engine/SDLC Image Pull Failures**
- **Problem**: `finos/legend-engine:3.0.0` and `finos/legend-sdlc:3.0.0` not publicly accessible
- **Impact**: Backend services cannot start
- **Solutions**:
  1. Use FINOS Helm charts: `helm install legend finos/legend`
  2. Contact FINOS for image access
  3. Build custom images from source

### **Issue 2: Resource Constraints (RESOLVED)**
- **Problem**: AKS cluster had insufficient CPU resources
- **Solution**: Scaled cluster from 2 to 3 nodes
- **Current Status**: ✅ Resolved

### **Issue 3: Port Configuration (RESOLVED)**
- **Problem**: Legend Studio configured for port 9000, actual port 8080
- **Solution**: Updated service configuration
- **Current Status**: ✅ Resolved

## 🔍 **Monitoring & Health Checks**

### **Health Check Commands**
```bash
# Check all pods
kubectl get pods -n legend-system

# Check services
kubectl get services -n legend-system

# Check pod logs
kubectl logs <pod-name> -n legend-system

# Check pod details
kubectl describe pod <pod-name> -n legend-system

# Check cluster resources
kubectl top nodes
kubectl top pods -n legend-system
```

### **Service Health Endpoints**
- **Legend Studio**: http://20.242.235.80 (should return HTTP 200)
- **MongoDB**: Internal only, check pod status
- **Legend Engine**: Internal only, check pod status
- **Legend SDLC**: Internal only, check pod status

## 🛠️ **Troubleshooting Guide**

### **Common Problems & Solutions**

#### **Problem: Pod in Pending Status**
```bash
# Check resource constraints
kubectl describe pod <pod-name> -n legend-system | grep -A 10 "Events:"

# Check node resources
kubectl top nodes
kubectl describe node <node-name>
```

#### **Problem: Image Pull Failures**
```bash
# Check image pull errors
kubectl describe pod <pod-name> -n legend-system | grep -A 5 "Failed"

# Verify image exists
docker pull <image-name>
```

#### **Problem: Service Not Accessible**
```bash
# Check service configuration
kubectl get service <service-name> -n legend-system -o yaml

# Check endpoints
kubectl get endpoints <service-name> -n legend-system
```

#### **Problem: MongoDB Connection Issues**
```bash
# Check MongoDB pod status
kubectl get pods -n legend-system | grep mongodb

# Check MongoDB logs
kubectl logs <mongodb-pod-name> -n legend-system

# Test connection from within cluster
kubectl run --rm -it --restart=Never --image=mongo:4.4 mongo-test -- mongo mongodb:27017
```

## 🔧 **Maintenance Operations**

### **Scaling Operations**
```bash
# Scale AKS cluster
az aks scale --resource-group rs-finos-legend --name aks-legend --node-count <number>

# Scale deployments
kubectl scale deployment <deployment-name> --replicas=<number> -n legend-system
```

### **Update Operations**
```bash
# Update Helm charts
helm repo update
helm upgrade <release-name> <chart-name> -n <namespace>

# Update deployments
kubectl set image deployment/<deployment-name> <container-name>=<new-image> -n legend-system
```

### **Backup Operations**
```bash
# Backup MongoDB data
kubectl exec <mongodb-pod-name> -n legend-system -- mongodump --out=/tmp/backup

# Backup configuration
kubectl get all -n legend-system -o yaml > backup-$(date +%Y%m%d).yaml
```

## 📚 **Deployment Scripts Reference**

### **Available Scripts**
1. **`deploy-legend-juju-azure.sh`** - Full deployment with Juju approach
2. **`deploy-legend-simple-azure.sh`** - Simplified deployment
3. **`deploy-legend-minimal.sh`** - Minimal resource deployment
4. **`deploy-legend-correct-images.sh`** - Fixed image configuration
5. **`deploy-legend-no-mongo.sh`** - Deployment without MongoDB

### **Script Usage**
```bash
# Make script executable
chmod +x <script-name>.sh

# Run script
./<script-name>.sh

# Check script status
echo $?
```

## 🌐 **Network Configuration**

### **Internal Services**
- **MongoDB**: `mongodb:27017`
- **Legend Engine**: `legend-engine:6300`
- **Legend SDLC**: `legend-sdlc:6100`
- **Legend Studio**: `legend-studio:8080`

### **External Access**
- **Legend Studio**: http://20.242.235.80
- **Load Balancer**: Azure Standard Load Balancer
- **Public IP**: 20.242.235.80

### **Firewall & Security**
- **Network Policy**: None configured
- **Ingress Rules**: Basic HTTP access
- **TLS/HTTPS**: Not configured (HTTP only)

## 📈 **Performance Metrics**

### **Resource Usage**
- **CPU Requests**: 410m total
- **CPU Limits**: 600m total
- **Memory Requests**: 665Mi total
- **Memory Limits**: 1.3Gi total

### **Storage Usage**
- **MongoDB**: 5Gi persistent volume
- **Type**: Azure Managed Premium Disk
- **Performance**: High IOPS

## 🔐 **Security Configuration**

### **Authentication**
- **MongoDB**: Username/password (root/legend123456)
- **Legend Services**: No authentication configured
- **Kubernetes**: Azure AD integration

### **Network Security**
- **Pod-to-Pod**: Allowed within namespace
- **External Access**: LoadBalancer for Studio only
- **Internal Services**: ClusterIP (no external access)

## 🚀 **Next Steps for AI Agent**

### **Immediate Actions (Next 30 minutes)**
1. **Verify current system health**
2. **Check for any new errors**
3. **Monitor resource usage**

### **Short-term Actions (Next 2 hours)**
1. **Deploy missing Legend services** (Engine/SDLC)
2. **Configure service dependencies**
3. **Test full platform functionality**

### **Medium-term Actions (Next 24 hours)**
1. **Implement monitoring** (Grafana, Prometheus)
2. **Configure alerts** for critical issues
3. **Set up logging** aggregation
4. **Implement backup** strategies

## 📞 **Support Information**

### **Documentation Files**
- `AI_AGENT_SUPPORT_DOCUMENTATION.md` - This file
- `DEPLOYMENT_STATUS.md` - Current deployment status
- `FINAL_DEPLOYMENT_REPORT.md` - Comprehensive deployment report
- `JUJU_DEPLOYMENT_ANALYSIS.md` - Original deployment analysis

### **Key Commands Reference**
```bash
# Essential kubectl commands
kubectl get pods -n legend-system
kubectl get services -n legend-system
kubectl logs <pod-name> -n legend-system
kubectl describe pod <pod-name> -n legend-system

# Essential Azure commands
az aks get-credentials --resource-group rs-finos-legend --name aks-legend
az aks show --resource-group rs-finos-legend --name aks-legend
az aks scale --resource-group rs-finos-legend --name aks-legend --node-count <number>

# Essential Helm commands
helm list -n legend-system
helm upgrade <release> <chart> -n <namespace>
helm rollback <release> <revision> -n <namespace>
```

---

**Document Version**: 1.0  
**Last Updated**: August 17, 2025  
**AI Agent Support Level**: Comprehensive  
**Next Review**: After Legend Engine/SDLC deployment
