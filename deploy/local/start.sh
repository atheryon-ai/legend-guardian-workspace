#!/bin/bash

# Legend Local Development Startup Script
# Provides a simple way to start the local development environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker-compose version &> /dev/null; then
        print_error "Docker Compose is not installed."
        exit 1
    fi
    
    # Check for .env file
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_status "Please edit .env file with your GitLab OAuth credentials (optional)"
fi

# Load secrets if available (from parent directory)
if [ -f "../secrets.env" ]; then
    print_status "Loading secrets from secrets.env..."
    source "../secrets.env"
elif [ -f "../.env.local" ]; then
    print_status "Loading secrets from .env.local..."
    source "../.env.local"
else
    print_warning "No secrets file found. Using default values"
fi
    
    # Check port availability
    for port in 6100 6300 9000 27017; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Port $port is already in use"
        fi
    done
    
    print_success "Prerequisites check completed"
}

# Start services
start_services() {
    print_status "Starting Legend services..."
    
    case "${1:-all}" in
        all)
            print_status "Starting all services (including Guardian Agent)..."
            docker-compose --profile guardian up -d
            ;;
        core)
            print_status "Starting core Legend services..."
            docker-compose up -d mongodb legend-engine legend-sdlc legend-studio
            ;;
        guardian)
            print_status "Starting Guardian Agent only..."
            docker-compose --profile guardian up -d legend-guardian
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [all|core|guardian]"
            exit 1
            ;;
    esac
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for MongoDB
    print_status "Waiting for MongoDB..."
    until docker exec legend-mongodb mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; do
        sleep 2
    done
    print_success "MongoDB is ready"
    
    # Wait for Legend Engine
    print_status "Waiting for Legend Engine..."
    until curl -f http://localhost:6300/api/server/v1/info &>/dev/null 2>&1; do
        sleep 2
    done
    print_success "Legend Engine is ready"
    
    # Wait for Legend SDLC
    print_status "Waiting for Legend SDLC..."
    until curl -f http://localhost:6100/api/info &>/dev/null 2>&1; do
        sleep 2
    done
    print_success "Legend SDLC is ready"
    
    # Wait for Legend Studio
    print_status "Waiting for Legend Studio..."
    until curl -f http://localhost:9000 &>/dev/null 2>&1; do
        sleep 2
    done
    print_success "Legend Studio is ready"
}

# Show status
show_status() {
    echo ""
    print_success "Legend Platform is running!"
    echo ""
    echo "Access the services at:"
    echo "  📊 Legend Studio: http://localhost:9000"
    echo "  ⚙️  Legend Engine: http://localhost:6300"
    echo "  🔧 Legend SDLC: http://localhost:6100"
    echo "  💾 MongoDB: mongodb://localhost:27017"
    
    if docker ps | grep -q legend-guardian; then
        echo "  🤖 Guardian Agent: http://localhost:8000"
    fi
    
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f [service-name]"
    echo ""
    echo "To stop services:"
    echo "  docker-compose down"
}

# Main execution
main() {
    echo "========================================="
    echo "  Legend Local Development Environment"
    echo "========================================="
    echo ""
    
    check_prerequisites
    start_services "$1"
    wait_for_services
    show_status
}

main "$@"