#!/bin/bash

# Legend Local Development Startup Script
# Provides a simple way to start the local development environment

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common functions library
source "$SCRIPT_DIR/../lib/common-functions.sh"

# Load all configuration for local deployment
load_all_config "local"

# Check local prerequisites
check_local_prerequisites() {
    print_section "Checking Local Prerequisites"
    
    # Use common function to check Docker prerequisites
    check_prerequisites "local"
    
    # Check for local .env file (for docker-compose)
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            print_warning ".env file not found. Creating from template..."
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            print_status "Please edit .env file with your GitLab OAuth credentials (optional)"
        fi
    fi
    
    # Check port availability
    local ports=("$LEGEND_ENGINE_PORT" "$LEGEND_SDLC_PORT" "$LEGEND_STUDIO_PORT" "$MONGODB_PORT")
    check_ports_available "${ports[@]}"
    
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
    print_section "Legend Local Development Environment"
    echo ""
    
    check_local_prerequisites
    start_services "$1"
    wait_for_services
    show_status
}

main "$@"