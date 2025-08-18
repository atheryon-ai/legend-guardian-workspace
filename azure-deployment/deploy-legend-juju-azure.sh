#!/bin/bash

# Azure Legend Platform Deployment using FINOS Legend Kubernetes Manifests
# This script provides the same benefits as Juju deployment but with direct Azure control
# Based on the JUJU_DEPLOYMENT_ANALYSIS.md recommendations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="rs-finos-legend"
AKS_CLUSTER="aks-legend"
NAMESPACE="legend-system"
LEGEND_VERSION="3.0.0"

echo -e "${BLUE}🚀 Azure Legend Platform Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Resource Group: ${GREEN}$RESOURCE_GROUP${NC}"
echo -e "AKS Cluster: ${GREEN}$AKS_CLUSTER${NC}"
echo -e "Namespace: ${GREEN}$NAMESPACE${NC}"
echo -e "Legend Version: ${GREEN}$LEGEND_VERSION${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first:"
        echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first:"
        echo "   https://kubernetes.io/docs/tasks/tools/install-kubectl/"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        print_warning "Helm is not installed. Installing Helm..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    print_success "Prerequisites check completed"
}

# Login to Azure and get credentials
setup_azure() {
    print_status "Setting up Azure connection..."
    
    # Login to Azure
    az login --query "user.name" --output tsv > /dev/null 2>&1 || {
        print_status "Logging into Azure..."
        az login
    }
    
    # Get current subscription
    SUBSCRIPTION_ID=$(az account show --query "id" --output tsv)
    print_status "Using subscription: $SUBSCRIPTION_ID"
    
    # Get AKS credentials
    print_status "Getting AKS credentials..."
    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --overwrite-existing
    
    # Verify cluster connection
    print_status "Verifying cluster connection..."
    kubectl cluster-info > /dev/null 2>&1 || {
        print_error "Failed to connect to AKS cluster"
        exit 1
    }
    
    print_success "Azure setup completed"
}

# Create namespace and set up RBAC
setup_namespace() {
    print_status "Setting up Kubernetes namespace and RBAC..."
    
    # Create namespace
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Create service account for Legend
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: legend-service-account
  namespace: $NAMESPACE
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: legend-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints", "persistentvolumeclaims", "events", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses", "networkpolicies"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: legend-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: legend-cluster-role
subjects:
- kind: ServiceAccount
  name: legend-service-account
  namespace: $NAMESPACE
EOF
    
    print_success "Namespace and RBAC setup completed"
}

# Deploy MongoDB (using Azure Cosmos DB or MongoDB)
deploy_mongodb() {
    print_status "Deploying MongoDB..."
    
    # Check if MongoDB is already deployed
    if kubectl get deployment mongodb -n $NAMESPACE > /dev/null 2>&1; then
        print_warning "MongoDB already exists, skipping deployment"
        return
    fi
    
    # Deploy MongoDB using Helm
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    
    # Create MongoDB values file
    cat <<EOF > mongodb-values.yaml
architecture: replicaset
replicaCount: 1
auth:
  enabled: true
  rootPassword: "legend123456"
  database: legend
persistence:
  enabled: true
  size: 10Gi
  storageClass: "managed-premium"
service:
  type: ClusterIP
EOF
    
    # Install MongoDB
    helm install mongodb bitnami/mongodb \
        --namespace $NAMESPACE \
        --values mongodb-values.yaml \
        --wait \
        --timeout 10m
    
    print_success "MongoDB deployment completed"
}

# Deploy Legend Engine
deploy_legend_engine() {
    print_status "Deploying Legend Engine..."
    
    # Create Legend Engine deployment
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-engine
  namespace: $NAMESPACE
  labels:
    app: legend-engine
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
      serviceAccountName: legend-service-account
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
        - name: LEGEND_ENGINE_TEMP_DIR
          value: "/tmp"
        - name: LEGEND_ENGINE_OPENTELEMETRY_ENABLED
          value: "false"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 6300
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 6300
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: legend-engine
  namespace: $NAMESPACE
  labels:
    app: legend-engine
spec:
  type: ClusterIP
  ports:
  - port: 6300
    targetPort: 6300
    protocol: TCP
    name: http
  selector:
    app: legend-engine
EOF
    
    print_success "Legend Engine deployment completed"
}

# Deploy Legend SDLC
deploy_legend_sdlc() {
    print_status "Deploying Legend SDLC..."
    
    # Create Legend SDLC deployment
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-sdlc
  namespace: $NAMESPACE
  labels:
    app: legend-sdlc
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
      serviceAccountName: legend-service-account
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
        - name: LEGEND_SDLC_TEMP_DIR
          value: "/tmp"
        - name: LEGEND_SDLC_OPENTELEMETRY_ENABLED
          value: "false"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 6100
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 6100
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: legend-sdlc
  namespace: $NAMESPACE
  labels:
    app: legend-sdlc
spec:
  type: ClusterIP
  ports:
  - port: 6100
    targetPort: 6100
    protocol: TCP
    name: http
  selector:
    app: legend-sdlc
EOF
    
    print_success "Legend SDLC deployment completed"
}

# Deploy Legend Studio
deploy_legend_studio() {
    print_status "Deploying Legend Studio..."
    
    # Create Legend Studio deployment
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-studio
  namespace: $NAMESPACE
  labels:
    app: legend-studio
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
      serviceAccountName: legend-service-account
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
        - name: LEGEND_STUDIO_OPENTELEMETRY_ENABLED
          value: "false"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 9000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 9000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: legend-studio
  namespace: $NAMESPACE
  labels:
    app: legend-studio
spec:
  type: ClusterIP
  ports:
  - port: 9000
    targetPort: 9000
    protocol: TCP
    name: http
  selector:
    app: legend-studio
EOF
    
    print_success "Legend Studio deployment completed"
}

# Deploy Ingress Controller
deploy_ingress() {
    print_status "Deploying NGINX Ingress Controller..."
    
    # Add NGINX ingress repository
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install NGINX ingress controller
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
        --wait \
        --timeout 10m
    
    print_success "NGINX Ingress Controller deployment completed"
}

# Create Ingress rules
create_ingress() {
    print_status "Creating Ingress rules..."
    
    # Wait for ingress controller to be ready
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    
    # Create ingress rules
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: legend-ingress
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: legend-engine.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: legend-engine
            port:
              number: 6300
  - host: legend-sdlc.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: legend-sdlc
            port:
              number: 6100
  - host: legend-studio.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: legend-studio
            port:
              number: 9000
EOF
    
    print_success "Ingress rules created"
}

# Wait for all deployments to be ready
wait_for_deployments() {
    print_status "Waiting for all deployments to be ready..."
    
    # Wait for MongoDB
    kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n $NAMESPACE
    
    # Wait for Legend services
    kubectl wait --for=condition=available --timeout=300s deployment/legend-engine -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/legend-sdlc -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=300s deployment/legend-studio -n $NAMESPACE
    
    print_success "All deployments are ready"
}

# Get service information
get_service_info() {
    print_status "Getting service information..."
    
    # Get external IP for ingress
    EXTERNAL_IP=$(kubectl get service ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -n "$EXTERNAL_IP" ]; then
        print_success "External IP: $EXTERNAL_IP"
        echo ""
        echo -e "${GREEN}🎉 Legend Platform Deployment Complete!${NC}"
        echo "=========================================="
        echo ""
        echo -e "Legend Engine: ${BLUE}http://$EXTERNAL_IP${NC} (Host: legend-engine.local)"
        echo -e "Legend SDLC:   ${BLUE}http://$EXTERNAL_IP${NC} (Host: legend-sdlc.local)"
        echo -e "Legend Studio: ${BLUE}http://$EXTERNAL_IP${NC} (Host: legend-studio.local)"
        echo ""
        echo -e "${YELLOW}To access the services, add these entries to your /etc/hosts file:${NC}"
        echo "$EXTERNAL_IP legend-engine.local"
        echo "$EXTERNAL_IP legend-sdlc.local"
        echo "$EXTERNAL_IP legend-studio.local"
        echo ""
        echo -e "${GREEN}Next steps:${NC}"
        echo "1. Add the host entries to your /etc/hosts file"
        echo "2. Access Legend Studio at http://legend-studio.local"
        echo "3. Configure your GitLab OAuth app for Azure endpoints"
        echo "4. Set up TLS certificates for production use"
    else
        print_warning "External IP not yet available. Please wait a few minutes and run:"
        echo "kubectl get service ingress-nginx-controller -n ingress-nginx"
    fi
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting Legend Platform deployment on Azure AKS...${NC}"
    echo ""
    
    check_prerequisites
    setup_azure
    setup_namespace
    deploy_mongodb
    deploy_legend_engine
    deploy_legend_sdlc
    deploy_legend_studio
    deploy_ingress
    create_ingress
    wait_for_deployments
    get_service_info
    
    echo ""
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
