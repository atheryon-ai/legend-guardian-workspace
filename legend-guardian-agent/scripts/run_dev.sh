#!/bin/bash

# Development server startup script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Legend Guardian Agent in development mode...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    echo -e "${YELLOW}Warning: Python $REQUIRED_VERSION required, found $PYTHON_VERSION${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment variables from .env${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found, using defaults${NC}"
fi

# Check if Legend services are running
echo -e "${GREEN}Checking Legend services...${NC}"

check_service() {
    local name=$1
    local url=$2
    if curl -s -f -o /dev/null "$url"; then
        echo -e "  ✓ $name is running"
    else
        echo -e "  ${YELLOW}✗ $name is not responding at $url${NC}"
    fi
}

check_service "Legend Engine" "http://localhost:6300/api/server/v1/info"
check_service "Legend SDLC" "http://localhost:6100/api/info"
check_service "Legend Depot" "http://localhost:6200/api/info"

# Start the application
echo -e "${GREEN}Starting FastAPI application...${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}Health Check: http://localhost:8000/health${NC}"

# Run with auto-reload for development
uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log