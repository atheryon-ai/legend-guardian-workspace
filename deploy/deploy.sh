#!/bin/bash

# Master Deployment Script for Legend Platform
# Directs users to the appropriate deployment endpoint

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

echo "========================================="
echo "   Legend Platform Deployment Manager"
echo "========================================="
echo ""
echo "Choose your deployment target:"
echo ""
echo "1) Kubernetes (AKS/Local K8s)"
echo "2) Docker (Local development)"
echo "3) Azure (Infrastructure + AKS)"
echo "4) Exit"
echo ""

read -p "Select option (1-4): " choice

case $choice in
    1)
        print_info "Deploying to Kubernetes..."
        cd kubernetes
        ./deploy-all.sh
        ;;
    2)
        print_info "Starting Docker environment..."
        cd docker
        docker-compose up -d
        print_success "Docker services started!"
        echo "Access at: http://localhost:8000 (Guardian Agent)"
        ;;
    3)
        print_info "Deploying to Azure..."
        cd azure
        ./deploy-azure.bash
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option. Please run the script again."
        exit 1
        ;;
esac
