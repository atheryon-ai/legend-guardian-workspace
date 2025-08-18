#!/bin/bash

# Azure Legend Platform Deployment (No MongoDB)
# This script deploys the core Legend services without MongoDB dependency
# Based on the JUJU_DEPLOYMENT_ANALYSIS.md recommendations

set -e

# Configuration
RESOURCE_GROUP="rs-finos-legend"
AKS_CLUSTER="aks-legend"
NAMESPACE="legend-system"

echo "🚀 Azure Legend Platform Deployment (No MongoDB)"
echo "================================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "AKS Cluster: $AKS_CLUSTER"
echo "Namespace: $NAMESPACE"
echo ""

# Function to print status
print_status() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

print_error() {
    echo "[ERROR] $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check completed"
}

# Setup Azure connection
setup_azure() {
    print_status "Setting up Azure connection..."
    
    # Get AKS credentials
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --overwrite-existing
    
    # Verify cluster connection
    kubectl cluster-info > /dev/null 2>&1 || {
        print_error "Failed to connect to AKS cluster"
        exit 1
    }
    
    print_success "Azure setup completed"
}

# Create namespace
create_namespace() {
    print_status "Creating namespace..."
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespace created"
}

# Deploy Legend Engine
deploy_legend_engine() {
    print_status "Deploying Legend Engine..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-engine
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: legend-engine
  template:
    metadata:
      labels:
        app: legend-engine
    spec:
      containers:
      - name: legend-engine
        image: finos/legend-engine:latest
        ports:
        - containerPort: 6300
        env:
        - name: LEGEND_ENGINE_PORT
          value: "6300"
        - name: LEGEND_ENGINE_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: legend-engine
  namespace: $NAMESPACE
spec:
  type: ClusterIP
  ports:
  - port: 6300
    targetPort: 6300
    protocol: TCP
  selector:
    app: legend-engine
EOF
    
    print_success "Legend Engine deployed"
}

# Deploy Legend SDLC
deploy_legend_sdlc() {
    print_status "Deploying Legend SDLC..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-sdlc
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: legend-sdlc
  template:
    metadata:
      labels:
        app: legend-sdlc
    spec:
      containers:
      - name: legend-sdlc
        image: finos/legend-sdlc:latest
        ports:
        - containerPort: 6100
        env:
        - name: LEGEND_SDLC_PORT
          value: "6100"
        - name: LEGEND_SDLC_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: legend-sdlc
  namespace: $NAMESPACE
spec:
  type: ClusterIP
  ports:
  - port: 6100
    targetPort: 6100
    protocol: TCP
  selector:
    app: legend-sdlc
EOF
    
    print_success "Legend SDLC deployed"
}

# Deploy Legend Studio
deploy_legend_studio() {
    print_status "Deploying Legend Studio..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-studio
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: legend-studio
  template:
    metadata:
      labels:
        app: legend-studio
    spec:
      containers:
      - name: legend-studio
        image: finos/legend-studio:latest
        ports:
        - containerPort: 9000
        env:
        - name: LEGEND_STUDIO_PORT
          value: "9000"
        - name: LEGEND_STUDIO_HOST
          value: "0.0.0.0"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: legend-studio
  namespace: $NAMESPACE
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 9000
    protocol: TCP
  selector:
    app: legend-studio
EOF
    
    print_success "Legend Studio deployed"
}

# Wait for deployments
wait_for_deployments() {
    print_status "Waiting for deployments to be ready..."
    
    # Wait for Legend services
    kubectl wait --for=condition=available --timeout=300s deployment/legend-engine -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/legend-sdlc -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/legend-studio -n $NAMESPACE
    
    print_success "All deployments are ready"
}

# Show status
show_status() {
    print_status "Deployment status:"
    echo ""
    kubectl get pods -n $NAMESPACE
    echo ""
    kubectl get services -n $NAMESPACE
    echo ""
    
    # Get external IP for Studio
    EXTERNAL_IP=$(kubectl get service legend-studio -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")
    
    if [ "$EXTERNAL_IP" != "Pending..." ] && [ -n "$EXTERNAL_IP" ]; then
        echo "🎉 Legend Platform Deployment Complete!"
        echo "====================================="
        echo ""
        echo "Legend Studio is accessible at: http://$EXTERNAL_IP"
        echo ""
        echo "Next steps:"
        echo "1. Access Legend Studio at http://$EXTERNAL_IP"
        echo "2. Configure your GitLab OAuth app"
        echo "3. Set up proper domain names and TLS"
        echo "4. Deploy MongoDB when ready"
    else
        echo "Legend Studio external IP is still pending..."
        echo "Run 'kubectl get service legend-studio -n $NAMESPACE' to check status"
    fi
}

# Main deployment
main() {
    echo "Starting Legend Platform deployment on Azure AKS (No MongoDB)..."
    echo ""
    
    check_prerequisites
    setup_azure
    create_namespace
    deploy_legend_engine
    deploy_legend_sdlc
    deploy_legend_studio
    wait_for_deployments
    show_status
    
    echo ""
    print_success "Deployment completed!"
}

# Run main function
main "$@"
