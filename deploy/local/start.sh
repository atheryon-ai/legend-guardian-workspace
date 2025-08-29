#!/bin/bash

# Legend Guardian Agent - Local Development Start Script

set -e

echo "🚀 Starting Legend Guardian Agent with full Legend stack..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
        echo "📝 Please edit .env with your configuration before continuing"
        echo "   Key variables to set: API_KEY, PROJECT_ID, WORKSPACE_ID"
        read -p "Press Enter to continue after editing .env..."
    else
        echo "❌ No env.example file found. Please create .env manually."
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if ports are available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Port $port is already in use by another service"
        echo "   Please stop the service using port $port or change the port in docker-compose.yml"
        exit 1
    fi
}

echo "🔍 Checking if required ports are available..."
check_port 8000 "Legend Guardian Agent"
check_port 9000 "Legend Studio"
check_port 6300 "Legend Engine"
check_port 6100 "Legend SDLC"
check_port 6200 "Legend Depot"
check_port 27017 "MongoDB"
check_port 5432 "PostgreSQL"

echo "✅ All ports are available"

# Start services with full profile
echo "🐳 Starting Docker Compose with full profile..."
docker compose --profile full up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start up..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker compose --profile full ps

echo ""
echo "🎉 Legend Guardian Agent is starting up!"
echo ""
echo "📱 Access your services:"
echo "   • Legend Guardian Agent: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Legend Studio: http://localhost:9000"
echo "   • Legend Engine: http://localhost:6300"
echo "   • Legend SDLC: http://localhost:6100"
echo "   • Legend Depot: http://localhost:6200"
echo ""
echo "📋 Useful commands:"
echo "   • View logs: docker compose --profile full logs -f"
echo "   • Stop services: docker compose --profile full down"
echo "   • Restart: docker compose --profile full restart"
echo ""
echo "🔍 Monitor startup progress:"
echo "   docker compose --profile full logs -f legend-guardian-agent"
