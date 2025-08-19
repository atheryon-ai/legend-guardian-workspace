# 🔧 AI Agent Troubleshooting Flow - Azure Legend Platform

## 📋 **Purpose**
This document provides AI Agents with a systematic approach to diagnose and resolve issues in the Azure Legend platform deployment.

## 🎯 **Troubleshooting Methodology**

### **1. Information Gathering Phase**
- Collect current system state
- Identify affected components
- Gather error messages and logs
- Understand user impact

### **2. Analysis Phase**
- Analyze collected information
- Identify root cause
- Determine solution approach
- Assess risk and impact

### **3. Resolution Phase**
- Execute solution
- Verify resolution
- Monitor system health
- Document actions taken

## 🚨 **Critical Issue Classification**

### **Severity Levels**
- **🔴 Critical**: System completely down, no services accessible
- **🟡 High**: Major functionality impaired, some services down
- **🟢 Medium**: Minor functionality issues, services degraded
- **🔵 Low**: Cosmetic issues, no functional impact

### **Response Times**
- **Critical**: Immediate (within 5 minutes)
- **High**: Within 30 minutes
- **Medium**: Within 2 hours
- **Low**: Within 24 hours

## 🔍 **System Health Check Flow**

### **Step 1: Overall System Status**
```bash
# Check all pods status
kubectl get pods -n legend-system

# Check all services
kubectl get services -n legend-system

# Check nodes
kubectl get nodes
```

### **Step 2: Identify Issues**
```bash
# Look for pods not in Running state
kubectl get pods -n legend-system | grep -v "Running"

# Look for services without endpoints
kubectl get endpoints -n legend-system

# Check for resource issues
kubectl top nodes
kubectl top pods -n legend-system
```

### **Step 3: Categorize Problems**
- **Pod Issues**: ImagePullBackOff, Pending, CrashLoopBackOff
- **Service Issues**: No endpoints, connection failures
- **Resource Issues**: Insufficient CPU/memory, node pressure
- **Network Issues**: DNS resolution, connectivity problems

## 🛠️ **Common Issue Resolution Flows**

### **Flow 1: Pod Image Pull Failures**

#### **Symptoms**
- Pod status: `ImagePullBackOff` or `ErrImagePull`
- Error messages about failed image pulls
- Pods stuck in non-running state

#### **Diagnosis Steps**
```bash
# 1. Check pod events
kubectl describe pod <pod-name> -n legend-system | grep -A 10 "Events:"

# 2. Check image pull errors
kubectl describe pod <pod-name> -n legend-system | grep -A 5 "Failed"

# 3. Verify image exists
docker pull <image-name>
```

#### **Resolution Steps**
```bash
# Option 1: Use alternative image
kubectl set image deployment/<deployment-name> <container-name>=<alternative-image> -n legend-system

# Option 2: Use FINOS Helm charts
helm repo add finos https://finos.github.io/helm-charts
helm install legend finos/legend --namespace legend-system

# Option 3: Build custom image
# (Requires source code and build process)
```

#### **Verification**
```bash
# Check pod status
kubectl get pods -n legend-system

# Check pod logs
kubectl logs <pod-name> -n legend-system
```

### **Flow 2: Resource Constraints**

#### **Symptoms**
- Pods stuck in `Pending` status
- Error messages about insufficient resources
- High resource usage on nodes

#### **Diagnosis Steps**
```bash
# 1. Check node resources
kubectl top nodes

# 2. Check pod resource requests
kubectl describe pod <pod-name> -n legend-system | grep -A 10 "Allocated resources"

# 3. Check node capacity
kubectl describe node <node-name> | grep -A 5 "Capacity"
```

#### **Resolution Steps**
```bash
# Option 1: Scale AKS cluster
az aks scale --resource-group rs-finos-legend --name aks-legend --node-count <number>

# Option 2: Reduce resource requests
kubectl patch deployment <deployment-name> -n legend-system -p '{"spec":{"template":{"spec":{"containers":[{"name":"<container-name>","resources":{"requests":{"cpu":"100m","memory":"256Mi"}}}]}}}}'

# Option 3: Scale down other deployments
kubectl scale deployment <deployment-name> --replicas=1 -n legend-system
```

#### **Verification**
```bash
# Wait for scaling to complete
kubectl get nodes

# Check pod scheduling
kubectl get pods -n legend-system
```

### **Flow 3: Service Connectivity Issues**

#### **Symptoms**
- Services not accessible
- Connection timeouts
- DNS resolution failures

#### **Diagnosis Steps**
```bash
# 1. Check service configuration
kubectl get service <service-name> -n legend-system -o yaml

# 2. Check service endpoints
kubectl get endpoints <service-name> -n legend-system

# 3. Test connectivity from within cluster
kubectl run --rm -it --restart=Never --image=busybox test-connection -- wget -O- <service-name>:<port>
```

#### **Resolution Steps**
```bash
# Option 1: Fix service selector
kubectl patch service <service-name> -n legend-system -p '{"spec":{"selector":{"app":"<correct-label>"}}}'

# Option 2: Fix port configuration
kubectl patch service <service-name> -n legend-system -p '{"spec":{"ports":[{"port":<correct-port>,"targetPort":<correct-target-port>}]}}'

# Option 3: Restart deployment
kubectl rollout restart deployment <deployment-name> -n legend-system
```

#### **Verification**
```bash
# Check service endpoints
kubectl get endpoints <service-name> -n legend-system

# Test connectivity
kubectl run --rm -it --restart=Never --image=busybox test-connection -- wget -O- <service-name>:<port>
```

### **Flow 4: Database Issues**

#### **Symptoms**
- MongoDB connection failures
- Database errors in application logs
- Data persistence issues

#### **Diagnosis Steps**
```bash
# 1. Check MongoDB pod status
kubectl get pods -n legend-system | grep mongodb

# 2. Check MongoDB logs
kubectl logs <mongodb-pod-name> -n legend-system

# 3. Test database connectivity
kubectl run --rm -it --restart=Never --image=mongo:4.4 mongo-test -- mongo mongodb:27017
```

#### **Resolution Steps**
```bash
# Option 1: Restart MongoDB
kubectl rollout restart deployment mongodb -n legend-system

# Option 2: Check storage issues
kubectl describe pvc -n legend-system

# Option 3: Recreate MongoDB
helm uninstall mongodb -n legend-system
helm install mongodb bitnami/mongodb --namespace legend-system --set architecture=standalone --set auth.enabled=true --set auth.rootPassword="legend123456"
```

#### **Verification**
```bash
# Check MongoDB status
kubectl get pods -n legend-system | grep mongodb

# Test connection
kubectl run --rm -it --restart=Never --image=mongo:4.4 mongo-test -- mongo mongodb:27017/admin -u root -p legend123456
```

## 🔄 **Escalation Flow**

### **Level 1: AI Agent Resolution**
- Use troubleshooting flows
- Execute standard commands
- Apply known solutions
- Document actions taken

### **Level 2: Advanced Troubleshooting**
- Deep log analysis
- Network packet capture
- Performance profiling
- Configuration analysis

### **Level 3: Expert Intervention**
- Contact system administrators
- Engage Azure support
- Contact FINOS Legend team
- Consider architecture changes

## 📊 **Monitoring and Alerting**

### **Key Metrics to Monitor**
- **Pod Status**: All pods should be Running
- **Service Health**: All services should have endpoints
- **Resource Usage**: CPU/memory should be below 80%
- **Response Times**: Services should respond within 5 seconds
- **Error Rates**: Should be below 1%

### **Alerting Thresholds**
```bash
# Critical alerts
- Any pod not Running for >5 minutes
- Any service without endpoints for >2 minutes
- Node CPU usage >90% for >5 minutes
- Node memory usage >95% for >2 minutes

# Warning alerts
- Pod restart count >3 in 1 hour
- Service response time >10 seconds
- Resource usage >80% for >10 minutes
```

## 📝 **Documentation Requirements**

### **Issue Documentation**
- **Issue ID**: Unique identifier
- **Description**: Clear problem statement
- **Impact**: User/system impact assessment
- **Root Cause**: Identified cause
- **Resolution**: Steps taken to resolve
- **Prevention**: Measures to prevent recurrence

### **Action Logging**
```bash
# Log all actions taken
echo "$(date): Executed command: kubectl get pods -n legend-system" >> troubleshooting.log

# Capture command outputs
kubectl get pods -n legend-system > pod-status-$(date +%Y%m%d-%H%M%S).txt

# Document resolution steps
echo "$(date): Resolved issue by scaling AKS cluster to 3 nodes" >> resolution.log
```

## 🎯 **Success Criteria**

### **Resolution Success**
- All pods in Running state
- All services accessible
- Resource usage within limits
- No error messages in logs
- User functionality restored

### **Prevention Success**
- Root cause identified
- Monitoring improved
- Alerts configured
- Documentation updated
- Team knowledge enhanced

## 🚀 **Continuous Improvement**

### **Post-Resolution Actions**
1. **Analyze root cause** thoroughly
2. **Update monitoring** if gaps found
3. **Improve documentation** based on learnings
4. **Share knowledge** with team
5. **Implement preventive measures**

### **Knowledge Base Updates**
- Add new troubleshooting flows
- Update common issues list
- Improve resolution steps
- Add new monitoring metrics
- Update escalation procedures

---

**Document Version**: 1.0  
**Last Updated**: August 17, 2025  
**AI Agent Support Level**: Troubleshooting Flow  
**Usage**: Follow flows systematically, document all actions, escalate when needed
