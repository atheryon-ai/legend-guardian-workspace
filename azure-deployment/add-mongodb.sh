#!/bin/bash

# Add MongoDB to Existing Azure Legend Infrastructure
# This script adds MongoDB as required by FINOS Legend (not Cosmos DB)

set -e

# Configuration
RESOURCE_GROUP="rs-finos-legend"
LOCATION="eastus"
MONGO_DB_NAME="legend"
MONGO_NAMESPACE="legend"

echo "🐘 Adding MongoDB to Azure Legend Infrastructure"
echo "================================================"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Database Name: $MONGO_DB_NAME"
echo "Namespace: $MONGO_NAMESPACE"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
fi

# Check if resource group exists
echo "🔍 Checking if resource group exists..."
if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
    echo "❌ Resource group $RESOURCE_GROUP does not exist!"
    echo "Please run deploy-simple.sh first to create the infrastructure."
    exit 1
fi

echo "✅ Resource group $RESOURCE_GROUP found!"

# Check if AKS cluster exists
echo "🔍 Checking if AKS cluster exists..."
if ! az aks show --resource-group $RESOURCE_GROUP --name aks-legend &>/dev/null; then
    echo "❌ AKS cluster aks-legend does not exist!"
    echo "Please run deploy-simple.sh first to create the infrastructure."
    exit 1
fi

echo "✅ AKS cluster aks-legend found!"

# Get AKS credentials
echo "🔑 Getting AKS credentials..."
az aks get-credentials --resource-group $RESOURCE_GROUP --name aks-legend --overwrite-existing

# Create legend namespace if it doesn't exist
echo "📁 Creating legend namespace..."
kubectl create namespace $MONGO_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Generate MongoDB password
MONGO_PASSWORD=$(openssl rand -base64 32)
echo "🔑 Generated MongoDB password: $MONGO_PASSWORD"

# Create MongoDB deployment
echo "🚀 Creating MongoDB deployment..."
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: $MONGO_NAMESPACE
  labels:
    app: mongodb
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
        image: mongo:6.0
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: "admin"
        - name: MONGO_INITDB_ROOT_PASSWORD
          value: "$MONGO_PASSWORD"
        - name: MONGO_INITDB_DATABASE
          value: "$MONGO_DB_NAME"
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        - name: mongodb-init
          mountPath: /docker-entrypoint-initdb.d
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          tcpSocket:
            port: 27017
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          tcpSocket:
            port: 27017
          initialDelaySeconds: 5
          periodSeconds: 2
      volumes:
      - name: mongodb-data
        emptyDir: {}
      - name: mongodb-init
        configMap:
          name: mongodb-init
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: $MONGO_NAMESPACE
  labels:
    app: mongodb
spec:
  ports:
  - port: 27017
    targetPort: 27017
  selector:
    app: mongodb
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-init
  namespace: $MONGO_NAMESPACE
data:
  init.js: |
    db = db.getSiblingDB('$MONGO_DB_NAME');
    db.createUser({
      user: 'legend',
      pwd: '$MONGO_PASSWORD',
      roles: [
        { role: 'readWrite', db: '$MONGO_DB_NAME' },
        { role: 'dbAdmin', db: '$MONGO_DB_NAME' }
      ]
    });
EOF

echo "✅ MongoDB deployment created!"

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/mongodb -n $MONGO_NAMESPACE

echo "✅ MongoDB is ready!"

# Create Kubernetes secret for MongoDB connection
echo "🔐 Creating Kubernetes secret for MongoDB connection..."
kubectl create secret generic mongodb-connection \
    --from-literal=username="legend" \
    --from-literal=password="$MONGO_PASSWORD" \
    --from-literal=database="$MONGO_DB_NAME" \
    --from-literal=uri="mongodb://legend:$MONGO_PASSWORD@mongodb:27017/$MONGO_DB_NAME" \
    --namespace $MONGO_NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Kubernetes secret created!"

# Update the legend-config ConfigMap with MongoDB URI
echo "📝 Updating Legend configuration with MongoDB URI..."
kubectl patch configmap legend-config -n $MONGO_NAMESPACE -p "{\"data\":{\"MONGODB_URI\":\"mongodb://legend:$MONGO_PASSWORD@mongodb:27017/$MONGO_DB_NAME\"}}" --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Legend configuration updated!"

# Test MongoDB connection
echo "🧪 Testing MongoDB connection..."
kubectl run mongo-test --image=mongo:6.0 --rm -i --restart=Never --namespace $MONGO_NAMESPACE -- mongo "mongodb://legend:$MONGO_PASSWORD@mongodb:27017/$MONGO_DB_NAME" --eval "db.runCommand('ping')" 2>/dev/null | grep -q "ok.*1" && echo "✅ MongoDB connection test successful!" || echo "❌ MongoDB connection test failed!"

# Display results
echo ""
echo "🎉 MongoDB Added Successfully!"
echo "=============================="
echo "MongoDB Deployment: mongodb (in $MONGO_NAMESPACE namespace)"
echo "Database Name: $MONGO_DB_NAME"
echo "Username: legend"
echo "Password: $MONGO_PASSWORD"
echo ""
echo "📊 Connection Information:"
echo "Internal URI: mongodb://legend:$MONGO_PASSWORD@mongodb:27017/$MONGO_DB_NAME"
echo "Service Name: mongodb"
echo "Port: 27017"
echo ""
echo "🔐 Kubernetes Secret: mongodb-connection (in $MONGO_NAMESPACE namespace)"
echo "📝 ConfigMap: legend-config updated with MongoDB URI"
echo ""
echo "📝 Next Steps:"
echo "1. MongoDB is now running in your AKS cluster"
echo "2. Legend services can connect using the internal service name 'mongodb'"
echo "3. Continue with Legend application deployment"
echo ""
echo "💾 Save the MongoDB password securely!"
echo "🔗 The connection string is stored in Kubernetes secret: mongodb-connection"
echo ""
echo "🚀 Ready to deploy Legend with MongoDB support!"
echo ""
echo "⚠️  Note: This uses actual MongoDB (not Cosmos DB) as required by FINOS Legend"
echo "   to ensure full compatibility and avoid potential bugs."
