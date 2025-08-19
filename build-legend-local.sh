#!/bin/bash

set -e

echo "🚀 Building Legend Platform Locally"
echo "==================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Create a workspace for Legend builds
WORKSPACE="$HOME/legend-builds"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

print_status "Working directory: $WORKSPACE"

# Clone repositories if they don't exist
print_status "Cloning Legend repositories..."

if [ ! -d "legend-engine" ]; then
    print_status "Cloning legend-engine..."
    git clone https://github.com/finos/legend-engine.git
else
    print_warning "legend-engine already exists, pulling latest..."
    cd legend-engine && git pull && cd ..
fi

if [ ! -d "legend-sdlc" ]; then
    print_status "Cloning legend-sdlc..."
    git clone https://github.com/finos/legend-sdlc.git
else
    print_warning "legend-sdlc already exists, pulling latest..."
    cd legend-sdlc && git pull && cd ..
fi

if [ ! -d "legend-studio" ]; then
    print_status "Cloning legend-studio..."
    git clone https://github.com/finos/legend-studio.git
else
    print_warning "legend-studio already exists, pulling latest..."
    cd legend-studio && git pull && cd ..
fi

print_success "Repositories cloned/updated"

# Create Dockerfiles for each component
print_status "Creating optimized Dockerfiles..."

# Legend Engine Dockerfile
cat > legend-engine/Dockerfile.local <<'EOF'
FROM maven:3.8-openjdk-11 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer.Slf4jMavenTransferListener=warn

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=builder /app/legend-engine-server/target/legend-engine-server-*.jar /app/legend-engine.jar

# Create minimal config
RUN echo 'server:\n\
  applicationContextPath: /\n\
  applicationConnectors:\n\
    - type: http\n\
      port: 6060\n\
logging:\n\
  level: INFO\n\
swagger:\n\
  resourcePackage: org.finos.legend.engine.server.api\n\
pac4j:\n\
  bypassPaths:\n\
    - "/api/health"\n\
  clients: []\n\
  authorizers: {}' > /app/config.yml

EXPOSE 6060
CMD ["java", "-Xmx2g", "-Xms1g", "-jar", "/app/legend-engine.jar", "server", "/app/config.yml"]
EOF

# Legend SDLC Dockerfile
cat > legend-sdlc/Dockerfile.local <<'EOF'
FROM maven:3.8-openjdk-11 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests -Dorg.slf4j.simpleLogger.log.org.apache.maven.cli.transfer.Slf4jMavenTransferListener=warn

FROM openjdk:11-jre-slim
WORKDIR /app
COPY --from=builder /app/legend-sdlc-server/target/legend-sdlc-server-*.jar /app/legend-sdlc.jar

# Create minimal config
RUN echo 'server:\n\
  applicationContextPath: /\n\
  applicationConnectors:\n\
    - type: http\n\
      port: 7070\n\
logging:\n\
  level: INFO\n\
pac4j:\n\
  bypassPaths:\n\
    - "/api/health"\n\
  clients: []\n\
  authorizers: {}\n\
projectStructure:\n\
  extensionProvider:\n\
    org.finos.legend.sdlc.server.project.extension.DefaultProjectStructureExtensionProvider: {}\n\
features:\n\
  canCreateProject: true' > /app/config.yml

EXPOSE 7070
CMD ["java", "-Xmx2g", "-Xms1g", "-jar", "/app/legend-sdlc.jar", "server", "/app/config.yml"]
EOF

# Legend Studio Dockerfile
cat > legend-studio/Dockerfile.local <<'EOF'
FROM node:16 AS builder
WORKDIR /app
COPY . .
RUN npm install --legacy-peer-deps
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html

# Create config for connecting to backend services
RUN echo '{\n\
  "sdlc": {"url": "http://localhost:7070"},\n\
  "engine": {"url": "http://localhost:6060"}\n\
}' > /usr/share/nginx/html/config.json

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

print_success "Dockerfiles created"

# Build Docker images
print_status "Building Docker images (this will take some time)..."

print_status "Building legend-engine..."
cd legend-engine
docker build -f Dockerfile.local -t legend-engine:local . || {
    print_error "Failed to build legend-engine"
    exit 1
}
cd ..

print_status "Building legend-sdlc..."
cd legend-sdlc
docker build -f Dockerfile.local -t legend-sdlc:local . || {
    print_error "Failed to build legend-sdlc"
    exit 1
}
cd ..

print_status "Building legend-studio..."
cd legend-studio
docker build -f Dockerfile.local -t legend-studio:local . || {
    print_error "Failed to build legend-studio"
    exit 1
}
cd ..

print_success "All Docker images built successfully!"

# Create docker-compose for local testing
print_status "Creating docker-compose.yml for local testing..."

cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  mongodb:
    image: mongo:5.0
    container_name: legend-mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_DATABASE: legend
    volumes:
      - mongodb_data:/data/db
    networks:
      - legend-network

  legend-engine:
    image: legend-engine:local
    container_name: legend-engine
    ports:
      - "6060:6060"
    depends_on:
      - mongodb
    environment:
      MONGODB_URI: mongodb://mongodb:27017/legend
    networks:
      - legend-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6060/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  legend-sdlc:
    image: legend-sdlc:local
    container_name: legend-sdlc
    ports:
      - "7070:7070"
    depends_on:
      - mongodb
    environment:
      MONGODB_URI: mongodb://mongodb:27017/legend
    networks:
      - legend-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7070/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  legend-studio:
    image: legend-studio:local
    container_name: legend-studio
    ports:
      - "8080:80"
    depends_on:
      - legend-engine
      - legend-sdlc
    environment:
      LEGEND_SDLC_SERVER_URL: http://legend-sdlc:7070
      LEGEND_ENGINE_SERVER_URL: http://legend-engine:6060
    networks:
      - legend-network

networks:
  legend-network:
    driver: bridge

volumes:
  mongodb_data:
EOF

print_success "docker-compose.yml created"

echo ""
print_success "Build complete! Legend images are ready for local testing."
echo ""
echo "To test locally:"
echo "  cd $WORKSPACE"
echo "  docker-compose up -d"
echo ""
echo "To check status:"
echo "  docker-compose ps"
echo "  docker-compose logs -f"
echo ""
echo "Access services at:"
echo "  - Legend Studio: http://localhost:8080"
echo "  - Legend Engine: http://localhost:6060"
echo "  - Legend SDLC: http://localhost:7070"
echo "  - MongoDB: localhost:27017"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "Once verified, push to Azure ACR:"
echo "  docker tag legend-engine:local legendacr.azurecr.io/legend-engine:latest"
echo "  docker tag legend-sdlc:local legendacr.azurecr.io/legend-sdlc:latest"
echo "  docker tag legend-studio:local legendacr.azurecr.io/legend-studio:latest"
echo "  az acr login --name legendacr"
echo "  docker push legendacr.azurecr.io/legend-engine:latest"
echo "  docker push legendacr.azurecr.io/legend-sdlc:latest"
echo "  docker push legendacr.azurecr.io/legend-studio:latest"