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
    if ! check_ports_available "${ports[@]}"; then
        print_warning "Some ports are in use. Services may already be running."
    fi
    
    print_success "Prerequisites check completed"
}

# Start services
start_services() {
    local profile="${1:-all}"
    print_status "Starting Legend services (profile: $profile)..."
    
    cd "$SCRIPT_DIR"
    
    case "$profile" in
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
            print_error "Unknown profile: $profile"
            echo "Usage: $0 [all|core|guardian]"
            exit 1
            ;;
    esac
}

# Stop services
stop_services() {
    print_status "Stopping Legend services..."
    cd "$SCRIPT_DIR"
    docker-compose down
    print_success "Services stopped"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for MongoDB
    print_status "Waiting for MongoDB..."
    local mongo_ready=false
    for i in {1..30}; do
        if docker exec legend-mongodb mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
            mongo_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$mongo_ready" = true ]; then
        print_success "MongoDB is ready"
    else
        print_warning "MongoDB may not be fully ready"
    fi
    
    # Wait for Legend Engine
    print_status "Waiting for Legend Engine..."
    local engine_ready=false
    for i in {1..30}; do
        if curl -f http://localhost:$LEGEND_ENGINE_PORT/api/server/v1/info &>/dev/null 2>&1; then
            engine_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$engine_ready" = true ]; then
        print_success "Legend Engine is ready"
    else
        print_warning "Legend Engine may not be fully ready"
    fi
    
    # Wait for Legend SDLC
    print_status "Waiting for Legend SDLC..."
    local sdlc_ready=false
    for i in {1..30}; do
        if curl -f http://localhost:$LEGEND_SDLC_PORT/api/info &>/dev/null 2>&1; then
            sdlc_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$sdlc_ready" = true ]; then
        print_success "Legend SDLC is ready"
    else
        print_warning "Legend SDLC may not be fully ready"
    fi
    
    # Wait for Legend Studio
    print_status "Waiting for Legend Studio..."
    local studio_ready=false
    for i in {1..30}; do
        if curl -f http://localhost:$LEGEND_STUDIO_PORT &>/dev/null 2>&1; then
            studio_ready=true
            break
        fi
        sleep 2
    done
    
    if [ "$studio_ready" = true ]; then
        print_success "Legend Studio is ready"
    else
        print_warning "Legend Studio may not be fully ready"
    fi
}

# Show status
show_status() {
    print_section "Legend Platform Status"
    
    cd "$SCRIPT_DIR"
    docker-compose ps
    
    echo ""
    print_success "Legend Platform is running!"
    echo ""
    echo "Access the services at:"
    echo "  📊 Legend Studio: $LEGEND_STUDIO_URL"
    echo "  ⚙️  Legend Engine: $LEGEND_ENGINE_URL"
    echo "  🔧 Legend SDLC: $LEGEND_SDLC_URL"
    echo "  💾 MongoDB: mongodb://localhost:$MONGODB_PORT"
    
    if docker ps | grep -q legend-guardian; then
        echo "  🤖 Guardian Agent: http://localhost:$LEGEND_API_PORT"
    fi
    
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f [service-name]"
    echo ""
    echo "To stop services:"
    echo "  $0 stop"
}

# Show configuration
show_config() {
    print_section "Local Configuration"
    echo "Environment: $DEPLOYMENT_ENV"
    echo "MongoDB URI: $MONGODB_URI"
    echo "Legend Engine URL: $LEGEND_ENGINE_URL"
    echo "Legend SDLC URL: $LEGEND_SDLC_URL"
    echo "Legend Studio URL: $LEGEND_STUDIO_URL"
    echo "Guardian API Key: $LEGEND_API_KEY"
    echo "Engine Memory Limit: $ENGINE_MEMORY_LIMIT"
    echo "Java Options: $ENGINE_JAVA_OPTS"
}

# View logs
view_logs() {
    local service="${1:-}"
    
    cd "$SCRIPT_DIR"
    
    if [ -z "$service" ]; then
        print_status "Following logs for all services..."
        docker-compose logs -f
    else
        print_status "Following logs for $service..."
        docker-compose logs -f "$service"
    fi
}

# Main execution
main() {
    case "${1:-start}" in
        start)
            print_section "Legend Local Development Environment"
            echo ""
            check_local_prerequisites
            start_services "${2:-all}"
            wait_for_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            start_services "${2:-all}"
            wait_for_services
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            view_logs "$2"
            ;;
        config)
            show_config
            ;;
        validate)
            "$SCRIPT_DIR/../validate-config.sh" local
            ;;
        *)
            echo "Usage: $0 [start|stop|restart|status|logs|config|validate] [profile|service]"
            echo ""
            echo "Commands:"
            echo "  start [all|core|guardian] - Start services (default: all)"
            echo "  stop                      - Stop all services"
            echo "  restart [all|core|guardian] - Restart services"
            echo "  status                    - Show service status"
            echo "  logs [service]           - View logs (all services if none specified)"
            echo "  config                   - Show configuration"
            echo "  validate                 - Validate configuration"
            echo ""
            echo "Profiles:"
            echo "  all      - All services including Guardian Agent"
            echo "  core     - Only core Legend services"
            echo "  guardian - Only Guardian Agent"
            exit 1
            ;;
    esac
}

main "$@"