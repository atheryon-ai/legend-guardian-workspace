#!/bin/bash

set -e

echo "🚀 Pushing Legend Images to Azure Container Registry"
echo "===================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Load configuration from environment
if [ -f ".env.azure" ]; then
    source .env.azure
elif [ -f ".env.local" ]; then
    source .env.local
else
    echo "No environment file found (.env.azure or .env.local)"
    echo "Please run: deploy/secrets/setup.sh --env azure"
    exit 1
fi

# Use environment variables or defaults
ACR_NAME="${AZURE_ACR_NAME:-legendacr}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rs-finos-legend}"

# Check if logged into Azure
print_status "Checking Azure login..."
if ! az account show &>/dev/null; then
    print_error "Not logged into Azure. Please run 'az login' first."
    exit 1
fi

# Check if ACR exists
print_status "Checking Azure Container Registry..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv 2>/dev/null)

if [ -z "$ACR_LOGIN_SERVER" ]; then
    print_status "Creating Azure Container Registry: $ACR_NAME..."
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
    ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
fi

print_status "ACR Login Server: $ACR_LOGIN_SERVER"

# Login to ACR
print_status "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

# Check if local images exist
print_status "Checking local Docker images..."
if ! docker images | grep -q "legend-engine.*local"; then
    print_error "legend-engine:local not found. Please build it first."
    exit 1
fi

if ! docker images | grep -q "legend-sdlc.*local"; then
    print_error "legend-sdlc:local not found. Please build it first."
    exit 1
fi

if ! docker images | grep -q "legend-studio.*local"; then
    print_error "legend-studio:local not found. Please build it first."
    exit 1
fi

# Tag images for ACR
print_status "Tagging images for Azure Container Registry..."
docker tag legend-engine:local $ACR_LOGIN_SERVER/legend-engine:latest
docker tag legend-sdlc:local $ACR_LOGIN_SERVER/legend-sdlc:latest
docker tag legend-studio:local $ACR_LOGIN_SERVER/legend-studio:latest

# Push images to ACR
print_status "Pushing legend-engine to ACR..."
docker push $ACR_LOGIN_SERVER/legend-engine:latest

print_status "Pushing legend-sdlc to ACR..."
docker push $ACR_LOGIN_SERVER/legend-sdlc:latest

print_status "Pushing legend-studio to ACR..."
docker push $ACR_LOGIN_SERVER/legend-studio:latest

print_success "All images pushed successfully to ACR!"

# Update Kubernetes deployments
print_status "Creating updated Kubernetes deployment files..."

cat > ~/legend-builds/deploy-from-acr.yaml <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: legend-system
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: legend-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:5.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_DATABASE
          value: legend
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: legend-system
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-engine
  namespace: legend-system
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
        image: $ACR_LOGIN_SERVER/legend-engine:latest
        ports:
        - containerPort: 6060
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
  namespace: legend-system
spec:
  selector:
    app: legend-engine
  ports:
  - port: 6060
    targetPort: 6060
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-sdlc
  namespace: legend-system
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
        image: $ACR_LOGIN_SERVER/legend-sdlc:latest
        ports:
        - containerPort: 7070
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
  namespace: legend-system
spec:
  selector:
    app: legend-sdlc
  ports:
  - port: 7070
    targetPort: 7070
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legend-studio
  namespace: legend-system
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
        image: $ACR_LOGIN_SERVER/legend-studio:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: legend-studio
  namespace: legend-system
spec:
  selector:
    app: legend-studio
  ports:
  - port: 8080
    targetPort: 80
EOF

print_success "Deployment file created at: ~/legend-builds/deploy-from-acr.yaml"
echo ""
echo "To deploy to AKS, run:"
echo "  kubectl apply -f ~/legend-builds/deploy-from-acr.yaml"
echo ""
echo "To check deployment status:"
echo "  kubectl get pods -n legend-system"
echo ""
echo "To access services locally:"
echo "  kubectl port-forward -n legend-system svc/legend-studio 8080:8080"
echo "  kubectl port-forward -n legend-system svc/legend-engine 6060:6060"
echo "  kubectl port-forward -n legend-system svc/legend-sdlc 7070:7070"