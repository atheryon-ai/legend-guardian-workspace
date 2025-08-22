#!/bin/bash

# Script to pull latest FINOS Legend Docker images from Docker Hub
# These are official pre-built images, no local building required

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Pull latest images
pull_images() {
    print_status "Pulling latest FINOS Legend images from Docker Hub..."
    
    # Define images to pull with their latest tags
    # You can specify specific versions if needed for stability
    declare -a images=(
        "finos/legend-engine-server:latest"
        "finos/legend-sdlc-server:latest"
        "finos/legend-studio:latest"
        "finos/legend-shared-server:latest"
        "mongo:5.0"
    )
    
    # Pull each image
    for image in "${images[@]}"; do
        print_status "Pulling $image..."
        if docker pull "$image"; then
            print_success "Successfully pulled $image"
        else
            print_warning "Failed to pull $image, continuing..."
        fi
    done
}

# Check for specific version tags
check_versions() {
    print_status "Checking available versions..."
    
    echo ""
    echo "Available Legend Engine Server versions:"
    docker search finos/legend-engine-server --limit 5 --no-trunc
    
    echo ""
    echo "Available Legend SDLC Server versions:"
    docker search finos/legend-sdlc-server --limit 5 --no-trunc
    
    echo ""
    echo "Available Legend Studio versions:"
    docker search finos/legend-studio --limit 5 --no-trunc
}

# List pulled images
list_images() {
    print_status "Legend-related images available locally:"
    docker images | grep -E "finos/legend|mongo" || echo "No Legend images found locally"
}

# Main menu
main() {
    echo "========================================"
    echo "FINOS Legend Docker Image Manager"
    echo "========================================"
    
    check_docker
    
    case "${1:-pull}" in
        pull)
            pull_images
            list_images
            print_success "Images pulled successfully!"
            echo ""
            echo "To start the services, run:"
            echo "  ./start.sh"
            ;;
        versions)
            check_versions
            ;;
        list)
            list_images
            ;;
        clean)
            print_warning "This will remove all Legend images. Are you sure? (y/N)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                docker images | grep "finos/legend" | awk '{print $3}' | xargs -r docker rmi -f
                print_success "Legend images removed"
            else
                print_status "Cancelled"
            fi
            ;;
        *)
            echo "Usage: $0 [pull|versions|list|clean]"
            echo ""
            echo "Commands:"
            echo "  pull     - Pull latest Legend images from Docker Hub (default)"
            echo "  versions - Check available versions on Docker Hub"
            echo "  list     - List locally available Legend images"
            echo "  clean    - Remove all Legend images locally"
            exit 1
            ;;
    esac
}

main "$@"