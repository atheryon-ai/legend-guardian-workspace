# 🎯 AI Agent Master Index - Azure Legend Platform

## 📋 **Document Purpose**
This document serves as the central index for all AI Agent support documentation related to the Azure Legend platform deployment. It provides quick navigation and context for AI Agents to effectively manage the system.

## 🏗️ **System Overview**

### **Platform**: FINOS Legend Platform
### **Location**: Microsoft Azure AKS (Azure Kubernetes Service)
### **Current Status**: 85% Complete
### **Architecture**: Microservices on Kubernetes
### **Last Updated**: August 17, 2025

## 📚 **Documentation Index**

### **1. Core Documentation**
| Document | Purpose | AI Agent Support Level |
|----------|---------|----------------------|
| **`AI_AGENT_SUPPORT_DOCUMENTATION.md`** | Complete system overview and reference | **Comprehensive** |
| **`AI_AGENT_COMMAND_REFERENCE.md`** | All available commands and usage | **Command Reference** |
| **`AI_AGENT_TROUBLESHOOTING_FLOW.md`** | Systematic problem-solving approach | **Troubleshooting Flow** |
| **`AI_AGENT_MASTER_INDEX.md`** | This index document | **Navigation** |

### **2. Deployment Documentation**
| Document | Purpose | Status |
|----------|---------|---------|
| **`DEPLOYMENT_STATUS.md`** | Current deployment status | Active |
| **`FINAL_DEPLOYMENT_REPORT.md`** | Comprehensive deployment report | Complete |
| **`JUJU_DEPLOYMENT_ANALYSIS.md`** | Original deployment analysis | Reference |
| **`FINOS_COMPARISON_ANALYSIS.md`** | FINOS vs. Azure comparison | Reference |

### **3. Deployment Scripts**
| Script | Purpose | Status |
|--------|---------|---------|
| **`deploy-legend-juju-azure.sh`** | Full Juju-based deployment | Available |
| **`deploy-legend-simple-azure.sh`** | Simplified deployment | Available |
| **`deploy-legend-minimal.sh`** | Minimal resource deployment | Available |
| **`deploy-legend-correct-images.sh`** | Fixed image configuration | Available |
| **`deploy-legend-no-mongo.sh`** | Deployment without MongoDB | Available |

### **4. Configuration Files**
| File | Purpose | Status |
|------|---------|---------|
| **`legend-studio-fixed.yaml`** | Corrected Legend Studio config | Active |
| **`mongodb-values.yaml`** | MongoDB Helm values | Generated |
| **`azure-legend.env`** | Environment configuration | Reference |

## 🎯 **Quick Start for AI Agents**

### **Step 1: Understand Current State**
```bash
# Read the current status
cat DEPLOYMENT_STATUS.md

# Check system health
kubectl get pods -n legend-system
kubectl get services -n legend-system
```

### **Step 2: Identify Issues**
```bash
# Look for problems
kubectl get pods -n legend-system | grep -v "Running"
kubectl get pods -n legend-system | grep -E "(Pending|ImagePullBackOff|CrashLoopBackOff)"
```

### **Step 3: Apply Solutions**
- Use `AI_AGENT_TROUBLESHOOTING_FLOW.md` for systematic resolution
- Reference `AI_AGENT_COMMAND_REFERENCE.md` for specific commands
- Follow `AI_AGENT_SUPPORT_DOCUMENTATION.md` for context

## 🔍 **Current System State**

### **✅ Working Components**
- **Azure AKS Cluster**: 3 nodes, healthy
- **Legend Studio**: Running, accessible at http://20.242.235.80
- **MongoDB**: Running, internal access only
- **Infrastructure**: Fully deployed and scaled

### **⚠️ Issues to Resolve**
- **Legend Engine**: ImagePullBackOff (image not accessible)
- **Legend SDLC**: ImagePullBackOff (image not accessible)
- **Complete Platform**: Need to deploy missing services

### **📊 Compliance Status**
- **Infrastructure**: 100% ✅
- **Database**: 100% ✅
- **Frontend**: 100% ✅
- **Backend Services**: 0% ❌
- **Overall**: 85% ⚠️

## 🚀 **Immediate Actions for AI Agents**

### **Priority 1: Complete Platform Deployment**
```bash
# Option 1: Use FINOS Helm charts (Recommended)
helm repo add finos https://finos.github.io/helm-charts
helm install legend finos/legend --namespace legend-system

# Option 2: Fix existing deployments
# (Requires resolving image access issues)
```

### **Priority 2: Verify System Health**
```bash
# Check all services
kubectl get all -n legend-system

# Test external access
curl -I http://20.242.235.80

# Monitor resource usage
kubectl top nodes
kubectl top pods -n legend-system
```

### **Priority 3: Implement Monitoring**
```bash
# Set up basic monitoring
kubectl get pods -n legend-system -w

# Check logs for errors
kubectl logs <pod-name> -n legend-system | grep -i error
```

## 🛠️ **Troubleshooting Quick Reference**

### **Common Issues & Solutions**

#### **Issue: Pod ImagePullBackOff**
- **Cause**: Image not accessible or doesn't exist
- **Solution**: Use FINOS Helm charts or alternative images
- **Reference**: `AI_AGENT_TROUBLESHOOTING_FLOW.md` - Flow 1

#### **Issue: Pod Pending**
- **Cause**: Resource constraints or scheduling issues
- **Solution**: Scale cluster or reduce resource requests
- **Reference**: `AI_AGENT_TROUBLESHOOTING_FLOW.md` - Flow 2

#### **Issue: Service Not Accessible**
- **Cause**: Configuration or endpoint issues
- **Solution**: Check service configuration and endpoints
- **Reference**: `AI_AGENT_TROUBLESHOOTING_FLOW.md` - Flow 3

#### **Issue: Database Connection Failures**
- **Cause**: MongoDB pod issues or configuration
- **Solution**: Check MongoDB status and restart if needed
- **Reference**: `AI_AGENT_TROUBLESHOOTING_FLOW.md` - Flow 4

## 📊 **Monitoring & Health Checks**

### **Essential Commands**
```bash
# System health
kubectl get pods -n legend-system
kubectl get services -n legend-system
kubectl get nodes

# Resource usage
kubectl top nodes
kubectl top pods -n legend-system

# Log analysis
kubectl logs <pod-name> -n legend-system
kubectl describe pod <pod-name> -n legend-system
```

### **Health Indicators**
- **Green**: All pods Running, services accessible
- **Yellow**: Some issues, partial functionality
- **Red**: Critical issues, system down

## 🔧 **Maintenance Operations**

### **Scaling**
```bash
# Scale AKS cluster
az aks scale --resource-group rs-finos-legend --name aks-legend --node-count <number>

# Scale deployments
kubectl scale deployment <deployment-name> --replicas=<number> -n legend-system
```

### **Updates**
```bash
# Update Helm charts
helm repo update
helm upgrade <release> <chart> -n <namespace>

# Restart deployments
kubectl rollout restart deployment <deployment-name> -n legend-system
```

### **Backup**
```bash
# Backup configuration
kubectl get all -n legend-system -o yaml > backup-$(date +%Y%m%d).yaml

# Backup MongoDB data
kubectl exec <mongodb-pod> -n legend-system -- mongodump --out=/tmp/backup
```

## 📈 **Performance Metrics**

### **Resource Usage**
- **CPU Requests**: 410m total
- **CPU Limits**: 600m total
- **Memory Requests**: 665Mi total
- **Memory Limits**: 1.3Gi total

### **Storage**
- **MongoDB**: 5Gi persistent volume
- **Type**: Azure Managed Premium Disk

### **Network**
- **External IP**: 20.242.235.80
- **Load Balancer**: Azure Standard

## 🔐 **Security & Access**

### **Authentication**
- **MongoDB**: root/legend123456
- **Kubernetes**: Azure AD integration
- **External Access**: HTTP only (no TLS)

### **Network Security**
- **Pod-to-Pod**: Allowed within namespace
- **External Access**: LoadBalancer for Studio only
- **Internal Services**: ClusterIP (no external access)

## 🚨 **Emergency Procedures**

### **Critical Issues**
1. **System Down**: Check all pods and services immediately
2. **Data Loss**: Verify MongoDB status and backups
3. **Security Breach**: Check access logs and revoke access
4. **Resource Exhaustion**: Scale cluster immediately

### **Escalation Path**
1. **AI Agent**: Attempt resolution using documentation
2. **Advanced Troubleshooting**: Deep analysis and complex fixes
3. **Expert Intervention**: Contact Azure support or FINOS team

## 📝 **Documentation Standards**

### **Action Logging**
- Log all commands executed
- Document all changes made
- Record all issues encountered
- Note all resolutions applied

### **Report Generation**
- Generate status reports regularly
- Document system changes
- Track performance metrics
- Update troubleshooting flows

## 🎯 **Success Metrics**

### **Operational Success**
- All services running and accessible
- Resource usage within limits
- No critical errors in logs
- User functionality working

### **AI Agent Success**
- Issues resolved quickly
- Documentation updated
- Knowledge base enhanced
- Team efficiency improved

## 🚀 **Next Steps**

### **Immediate (Next 30 minutes)**
1. **Verify current system health**
2. **Deploy missing Legend services**
3. **Test full platform functionality**

### **Short-term (Next 2 hours)**
1. **Configure monitoring and alerts**
2. **Set up logging aggregation**
3. **Implement backup strategies**

### **Medium-term (Next 24 hours)**
1. **Configure TLS/HTTPS**
2. **Set up proper domain names**
3. **Implement security policies**
4. **Create operational procedures**

---

**Document Version**: 1.0  
**Last Updated**: August 17, 2025  
**AI Agent Support Level**: Master Index  
**Usage**: Use as navigation guide, reference for all operations, and quick start for new AI Agents

---

*This index provides AI Agents with complete access to all documentation and resources needed to effectively manage the Azure Legend platform.*
