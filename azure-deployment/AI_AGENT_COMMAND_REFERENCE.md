# 🤖 AI Agent Command Reference - Azure Legend Platform

## 📋 **Purpose**
This document provides AI Agents with a comprehensive reference of commands to manage, monitor, and troubleshoot the Azure Legend platform deployment.

## 🚀 **Quick Start Commands**

### **1. System Status Check**
```bash
# Check overall system health
kubectl get pods -n legend-system
kubectl get services -n legend-system
kubectl get nodes
```

### **2. Access Azure AKS**
```bash
# Get AKS credentials
az aks get-credentials --resource-group rs-finos-legend --name aks-legend --overwrite-existing

# Verify connection
kubectl cluster-info
```

## 🔍 **Monitoring Commands**

### **Pod Status Monitoring**
```bash
# Check all pods in namespace
kubectl get pods -n legend-system

# Check pods with wide output
kubectl get pods -n legend-system -o wide

# Watch pods in real-time
kubectl get pods -n legend-system -w

# Check specific pod status
kubectl get pod <pod-name> -n legend-system
```

### **Service Status Monitoring**
```bash
# Check all services
kubectl get services -n legend-system

# Check service details
kubectl describe service <service-name> -n legend-system

# Check service endpoints
kubectl get endpoints -n legend-system
```

### **Resource Usage Monitoring**
```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n legend-system

# Check node details
kubectl describe node <node-name>
```

## 📊 **Log Analysis Commands**

### **Pod Logs**
```bash
# Get recent logs
kubectl logs <pod-name> -n legend-system

# Follow logs in real-time
kubectl logs -f <pod-name> -n legend-system

# Get logs with timestamps
kubectl logs <pod-name> -n legend-system --timestamps

# Get logs from specific container
kubectl logs <pod-name> -c <container-name> -n legend-system

# Get logs from previous pod instance
kubectl logs <pod-name> -n legend-system --previous
```

### **Log Analysis Examples**
```bash
# Check for errors in Legend Studio
kubectl logs legend-studio-56796d4c95-s2wws -n legend-system | grep -i error

# Check MongoDB startup logs
kubectl logs mongodb-574898c447-rdbvb -n legend-system | grep -i "started"

# Check for failed image pulls
kubectl logs <pod-name> -n legend-system | grep -i "failed to pull"
```

## 🛠️ **Troubleshooting Commands**

### **Pod Issues**
```bash
# Get detailed pod information
kubectl describe pod <pod-name> -n legend-system

# Check pod events
kubectl describe pod <pod-name> -n legend-system | grep -A 20 "Events:"

# Check pod resource usage
kubectl describe pod <pod-name> -n legend-system | grep -A 10 "Allocated resources"
```

### **Service Issues**
```bash
# Check service configuration
kubectl get service <service-name> -n legend-system -o yaml

# Check service endpoints
kubectl get endpoints <service-name> -n legend-system

# Test service connectivity
kubectl run --rm -it --restart=Never --image=busybox test-connection -- wget -O- <service-name>:<port>
```

### **Network Issues**
```bash
# Check network policies
kubectl get networkpolicies -n legend-system

# Check ingress rules
kubectl get ingress -n legend-system

# Test DNS resolution
kubectl run --rm -it --restart=Never --image=busybox dns-test -- nslookup <service-name>
```

## 🔧 **Maintenance Commands**

### **Scaling Operations**
```bash
# Scale AKS cluster
az aks scale --resource-group rs-finos-legend --name aks-legend --node-count <number>

# Scale deployments
kubectl scale deployment <deployment-name> --replicas=<number> -n legend-system

# Check scaling status
kubectl get deployment <deployment-name> -n legend-system
```

### **Update Operations**
```bash
# Update Helm charts
helm repo update

# Upgrade Helm releases
helm upgrade <release-name> <chart-name> -n <namespace>

# Check Helm release status
helm status <release-name> -n <namespace>

# Rollback Helm releases
helm rollback <release-name> <revision> -n <namespace>
```

### **Restart Operations**
```bash
# Restart deployment (rolling restart)
kubectl rollout restart deployment <deployment-name> -n legend-system

# Check rollout status
kubectl rollout status deployment <deployment-name> -n legend-system

# Rollback deployment
kubectl rollout undo deployment <deployment-name> -n legend-system
```

## 🗄️ **Database Operations**

### **MongoDB Management**
```bash
# Check MongoDB pod status
kubectl get pods -n legend-system | grep mongodb

# Access MongoDB shell
kubectl exec -it <mongodb-pod-name> -n legend-system -- mongosh

# Backup MongoDB data
kubectl exec <mongodb-pod-name> -n legend-system -- mongodump --out=/tmp/backup

# Check MongoDB logs
kubectl logs <mongodb-pod-name> -n legend-system
```

### **Database Connection Testing**
```bash
# Test MongoDB connection from within cluster
kubectl run --rm -it --restart=Never --image=mongo:4.4 mongo-test -- mongo mongodb:27017

# Test MongoDB connection with authentication
kubectl run --rm -it --restart=Never --image=mongo:4.4 mongo-test -- mongo mongodb:27017/admin -u root -p legend123456
```

## 🌐 **Network Testing Commands**

### **Connectivity Testing**
```bash
# Test internal service connectivity
kubectl run --rm -it --restart=Never --image=busybox connectivity-test -- wget -O- legend-studio:8080

# Test external access
curl -I http://20.242.235.80

# Test port forwarding
kubectl port-forward --namespace legend-system svc/mongodb 27017:27017 &
```

### **DNS and Service Discovery**
```bash
# Check service DNS
kubectl run --rm -it --restart=Never --image=busybox dns-test -- nslookup legend-studio.legend-system.svc.cluster.local

# Check service endpoints
kubectl get endpoints -n legend-system
```

## 📈 **Performance Analysis Commands**

### **Resource Analysis**
```bash
# Check node capacity
kubectl describe nodes | grep -A 5 "Capacity"

# Check resource requests/limits
kubectl get pods -n legend-system -o custom-columns="NAME:.metadata.name,CPU_REQ:.spec.containers[*].resources.requests.cpu,MEMORY_REQ:.spec.containers[*].resources.requests.memory"

# Check resource usage over time
kubectl top pods -n legend-system --containers
```

### **Performance Monitoring**
```bash
# Check pod metrics
kubectl top pods -n legend-system

# Check node metrics
kubectl top nodes

# Monitor resource usage in real-time
watch kubectl top pods -n legend-system
```

## 🔐 **Security Commands**

### **Authentication & Authorization**
```bash
# Check service accounts
kubectl get serviceaccounts -n legend-system

# Check RBAC rules
kubectl get roles -n legend-system
kubectl get rolebindings -n legend-system

# Check cluster roles
kubectl get clusterroles | grep legend
kubectl get clusterrolebindings | grep legend
```

### **Secret Management**
```bash
# Check secrets
kubectl get secrets -n legend-system

# Check secret details
kubectl describe secret <secret-name> -n legend-system

# Decode secret values
kubectl get secret <secret-name> -n legend-system -o jsonpath='{.data.<key>}' | base64 -d
```

## 📋 **Configuration Management**

### **ConfigMap Operations**
```bash
# Check ConfigMaps
kubectl get configmaps -n legend-system

# Check ConfigMap details
kubectl describe configmap <configmap-name> -n legend-system

# Get ConfigMap data
kubectl get configmap <configmap-name> -n legend-system -o yaml
```

### **Deployment Configuration**
```bash
# Check deployment configuration
kubectl get deployment <deployment-name> -n legend-system -o yaml

# Check deployment history
kubectl rollout history deployment <deployment-name> -n legend-system

# Compare deployment versions
kubectl diff -f <deployment-file>.yaml
```

## 🚨 **Emergency Commands**

### **Critical Issues**
```bash
# Force delete stuck pods
kubectl delete pod <pod-name> -n legend-system --force --grace-period=0

# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Uncordon node
kubectl uncordon <node-name>

# Emergency restart of all deployments
kubectl rollout restart deployment --all -n legend-system
```

### **Recovery Operations**
```bash
# Restore from backup
kubectl apply -f backup-$(date +%Y%m%d).yaml

# Check cluster health
kubectl get componentstatuses

# Verify cluster connectivity
kubectl cluster-info dump
```

## 📚 **Documentation Commands**

### **Generate Reports**
```bash
# Generate system status report
kubectl get all -n legend-system -o wide > system-status-$(date +%Y%m%d-%H%M%S).txt

# Generate resource usage report
kubectl top nodes > node-resources-$(date +%Y%m%d-%H%M%S).txt
kubectl top pods -n legend-system > pod-resources-$(date +%Y%m%d-%H%M%S).txt

# Generate configuration backup
kubectl get all -n legend-system -o yaml > full-backup-$(date +%Y%m%d-%H%M%S).yaml
```

### **Export Information**
```bash
# Export service configurations
kubectl get services -n legend-system -o yaml > services-$(date +%Y%m%d-%H%M%S).yaml

# Export deployment configurations
kubectl get deployments -n legend-system -o yaml > deployments-$(date +%Y%m%d-%H%M%S).yaml

# Export namespace information
kubectl get namespace legend-system -o yaml > namespace-$(date +%Y%m%d-%H%M%S).yaml
```

## 🎯 **AI Agent Best Practices**

### **Command Execution Order**
1. **Always check current status first**
2. **Use appropriate namespaces**
3. **Verify changes with status commands**
4. **Document all actions taken**

### **Error Handling**
```bash
# Check command exit status
echo $?

# Capture command output
RESULT=$(kubectl get pods -n legend-system)
echo "Result: $RESULT"

# Handle errors gracefully
kubectl get pods -n legend-system || echo "Failed to get pods"
```

### **Resource Cleanup**
```bash
# Clean up temporary resources
kubectl delete pod --field-selector=status.phase=Succeeded -n legend-system

# Clean up completed jobs
kubectl delete job --field-selector=status.successful=1 -n legend-system
```

---

**Document Version**: 1.0  
**Last Updated**: August 17, 2025  
**AI Agent Support Level**: Command Reference  
**Usage**: Execute commands in order, check results, handle errors gracefully
