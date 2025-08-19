# Legend Guardian Agent - System Architecture

## 🏗️ **High-Level System Architecture**

```mermaid
graph TB
    subgraph "External Systems"
        GITLAB[GitLab Repository<br/>OAuth Authentication]
        AZURE[Azure AKS Cluster<br/>Production Environment]
    end
    
    subgraph "Legend Guardian Agent"
        API[FastAPI Server<br/>Port 8000]
        AGENT[Guardian Agent Core<br/>Intelligence Engine]
        MEMORY[Memory System<br/>Event History]
        CLIENTS[Service Clients]
    end
    
    subgraph "FINOS Legend Platform"
        ENGINE[Legend Engine<br/>Port 6060]
        SDLC[Legend SDLC<br/>Port 7070]
        STUDIO[Legend Studio<br/>Port 9000]
        MONGO[(MongoDB<br/>Port 27017)]
    end
    
    subgraph "Network & Security"
        INGRESS[Azure Ingress<br/>HTTPS/443]
        LOADBAL[Load Balancer<br/>Port 80/443]
        FIREWALL[Network Security Groups]
    end
    
    %% External connections
    GITLAB -->|OAuth Callback| INGRESS
    AZURE -->|Deployment| INGRESS
    
    %% Guardian Agent connections
    API -->|HTTP/8000| AGENT
    AGENT -->|Internal| MEMORY
    AGENT -->|HTTP Clients| CLIENTS
    
    %% Service connections
    CLIENTS -->|HTTP/6060| ENGINE
    CLIENTS -->|HTTP/7070| SDLC
    CLIENTS -->|HTTP/9000| STUDIO
    
    %% Database connections
    ENGINE -->|MongoDB| MONGO
    SDLC -->|MongoDB| MONGO
    
    %% Network flow
    INGRESS -->|HTTPS/443| LOADBAL
    LOADBAL -->|HTTP/80| API
    LOADBAL -->|HTTP/80| STUDIO
    LOADBAL -->|HTTP/80| ENGINE
    LOADBAL -->|HTTP/80| SDLC
    
    %% Security
    FIREWALL -->|Port Rules| INGRESS
    FIREWALL -->|Port Rules| LOADBAL
```

## 🔌 **Detailed Component Architecture**

```mermaid
graph LR
    subgraph "Client Layer"
        BROWSER[Web Browser<br/>Swagger UI]
        CLI[Command Line<br/>curl/scripts]
        APPS[External Apps<br/>API Integration]
    end
    
    subgraph "API Gateway Layer"
        FASTAPI[FastAPI Server<br/>Port 8000]
        AUTH[Authentication<br/>Bearer Token]
        CORS[CORS Middleware]
        ROUTES[API Routes]
    end
    
    subgraph "Agent Core Layer"
        GUARDIAN[Guardian Agent<br/>Main Intelligence]
        ANALYZER[Change Analyzer]
        PLANNER[Action Planner]
        EXECUTOR[Action Executor]
    end
    
    subgraph "Service Integration Layer"
        ENGINE_CLIENT[Engine Client<br/>HTTP/6060]
        SDLC_CLIENT[SDLC Client<br/>HTTP/7070]
        STUDIO_CLIENT[Studio Client<br/>HTTP/9000]
    end
    
    subgraph "Data Layer"
        MEMORY[Memory System<br/>Event Store]
        CONFIG[Configuration<br/>Environment]
        LOGS[Logging System]
    end
    
    subgraph "External Services"
        LEGEND_ENGINE[Legend Engine<br/>Port 6060]
        LEGEND_SDLC[Legend SDLC<br/>Port 7070]
        LEGEND_STUDIO[Legend Studio<br/>Port 9000]
        MONGODB[(MongoDB<br/>Port 27017)]
    end
    
    %% Client connections
    BROWSER -->|HTTP/8000| FASTAPI
    CLI -->|HTTP/8000| FASTAPI
    APPS -->|HTTP/8000| FASTAPI
    
    %% API Layer connections
    FASTAPI -->|Internal| AUTH
    FASTAPI -->|Internal| CORS
    FASTAPI -->|Internal| ROUTES
    
    %% Agent connections
    ROUTES -->|Internal| GUARDIAN
    GUARDIAN -->|Internal| ANALYZER
    GUARDIAN -->|Internal| PLANNER
    GUARDIAN -->|Internal| EXECUTOR
    
    %% Service connections
    GUARDIAN -->|Internal| ENGINE_CLIENT
    GUARDIAN -->|Internal| SDLC_CLIENT
    GUARDIAN -->|Internal| STUDIO_CLIENT
    
    %% External service calls
    ENGINE_CLIENT -->|HTTP/6060| LEGEND_ENGINE
    SDLC_CLIENT -->|HTTP/7070| LEGEND_SDLC
    STUDIO_CLIENT -->|HTTP/9000| LEGEND_STUDIO
    
    %% Data connections
    GUARDIAN -->|Internal| MEMORY
    GUARDIAN -->|Internal| CONFIG
    GUARDIAN -->|Internal| LOGS
    
    %% Database connections
    LEGEND_ENGINE -->|MongoDB| MONGODB
    LEGEND_SDLC -->|MongoDB| MONGODB
```

## 🌐 **Network Architecture & Ports**

```mermaid
graph TB
    subgraph "Internet"
        USERS[External Users<br/>Developers/Admins]
        GITLAB[GitLab OAuth<br/>Port 443]
    end
    
    subgraph "Azure AKS Cluster"
        subgraph "Public Ingress"
            INGRESS[Azure Ingress Controller<br/>Port 80/443]
        end
        
        subgraph "Legend Guardian Agent Namespace"
            GUARDIAN_POD[Guardian Agent Pod<br/>Port 8000]
            GUARDIAN_SVC[Guardian Agent Service<br/>Port 8000]
        end
        
        subgraph "Legend Platform Namespace"
            STUDIO_POD[Legend Studio Pod<br/>Port 9000]
            STUDIO_SVC[Legend Studio Service<br/>Port 9000]
            
            ENGINE_POD[Legend Engine Pod<br/>Port 6060]
            ENGINE_SVC[Legend Engine Service<br/>Port 6060]
            
            SDLC_POD[Legend SDLC Pod<br/>Port 7070]
            SDLC_SVC[Legend SDLC Service<br/>Port 7070]
        end
        
        subgraph "Database Namespace"
            MONGO_POD[MongoDB Pod<br/>Port 27017]
            MONGO_SVC[MongoDB Service<br/>Port 27017]
        end
    end
    
    %% External connections
    USERS -->|HTTPS/443| INGRESS
    GITLAB -->|OAuth/443| INGRESS
    
    %% Ingress routing
    INGRESS -->|HTTP/8000| GUARDIAN_SVC
    INGRESS -->|HTTP/9000| STUDIO_SVC
    INGRESS -->|HTTP/6060| ENGINE_SVC
    INGRESS -->|HTTP/7070| SDLC_SVC
    
    %% Service to Pod routing
    GUARDIAN_SVC -->|Internal| GUARDIAN_POD
    STUDIO_SVC -->|Internal| STUDIO_POD
    ENGINE_SVC -->|Internal| ENGINE_POD
    SDLC_SVC -->|Internal| SDLC_POD
    
    %% Internal service communication
    GUARDIAN_POD -->|HTTP/6060| ENGINE_POD
    GUARDIAN_POD -->|HTTP/7070| SDLC_POD
    GUARDIAN_POD -->|HTTP/9000| STUDIO_POD
    
    %% Database connections
    ENGINE_POD -->|MongoDB/27017| MONGO_POD
    SDLC_POD -->|MongoDB/27017| MONGO_POD
```

## 🔐 **Authentication & Security Architecture**

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Auth
    participant Guardian
    participant Legend
    
    Note over Client,Legend: Authentication Flow
    
    Client->>FastAPI: POST /api/v1/model/change<br/>Authorization: Bearer {api_key}
    FastAPI->>Auth: Verify API Key
    Auth->>Auth: Check VALID_API_KEYS
    Auth-->>FastAPI: Valid/Invalid
    
    alt Valid API Key
        FastAPI->>Guardian: Process Request
        Guardian->>Legend: HTTP Request<br/>LEGEND_API_KEY
        Legend-->>Guardian: Response
        Guardian-->>FastAPI: Result
        FastAPI-->>Client: Success Response
    else Invalid API Key
        FastAPI-->>Client: 401 Unauthorized
    end
```

## 📊 **Data Flow Architecture**

```mermaid
flowchart TD
    subgraph "Event Sources"
        GITLAB[GitLab Webhooks]
        MANUAL[Manual API Calls]
        SCHEDULED[Scheduled Checks]
    end
    
    subgraph "Guardian Agent Processing"
        RECEIVE[Event Reception]
        ANALYZE[Change Analysis]
        PLAN[Action Planning]
        EXECUTE[Action Execution]
        STORE[Memory Storage]
    end
    
    subgraph "Legend Platform Actions"
        VALIDATE[Model Validation]
        GENERATE[Service Generation]
        TEST[Test Execution]
        DEPLOY[Deployment]
    end
    
    subgraph "Output & Monitoring"
        LOGS[Logging]
        METRICS[Metrics]
        ALERTS[Alerts]
        REPORTS[Reports]
    end
    
    %% Data flow
    GITLAB --> RECEIVE
    MANUAL --> RECEIVE
    SCHEDULED --> RECEIVE
    
    RECEIVE --> ANALYZE
    ANALYZE --> PLAN
    PLAN --> EXECUTE
    EXECUTE --> STORE
    
    EXECUTE --> VALIDATE
    EXECUTE --> GENERATE
    EXECUTE --> TEST
    EXECUTE --> DEPLOY
    
    EXECUTE --> LOGS
    EXECUTE --> METRICS
    EXECUTE --> ALERTS
    EXECUTE --> REPORTS
```

## 🏷️ **Component Details**

### **Legend Guardian Agent**
- **Port**: 8000
- **Protocol**: HTTP/HTTPS
- **Framework**: FastAPI (Python)
- **Authentication**: Bearer Token (API Keys)
- **Features**: Model monitoring, validation, automation

### **Legend Engine**
- **Port**: 6060
- **Protocol**: HTTP
- **Purpose**: Model execution and validation
- **Database**: MongoDB (Port 27017)

### **Legend SDLC**
- **Port**: 7070
- **Protocol**: HTTP
- **Purpose**: Source control and lifecycle management
- **Database**: MongoDB (Port 27017)

### **Legend Studio**
- **Port**: 9000
- **Protocol**: HTTP
- **Purpose**: Web-based modeling interface
- **Authentication**: GitLab OAuth

### **MongoDB**
- **Port**: 27017
- **Protocol**: MongoDB Wire Protocol
- **Purpose**: Data persistence for all Legend services

### **Azure Ingress**
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Protocol**: HTTP/HTTPS
- **Purpose**: External access and load balancing

## 🔄 **Deployment Architecture**

```mermaid
graph LR
    subgraph "Development"
        DEV_API[Local API<br/>localhost:8000]
        DEV_ENGINE[Local Engine<br/>localhost:6060]
        DEV_SDLC[Local SDLC<br/>localhost:7070]
    end
    
    subgraph "Production (Azure AKS)"
        PROD_API[Azure API<br/>legend-guardian.azure-legend.com:8000]
        PROD_ENGINE[Azure Engine<br/>legend-engine.azure-legend.com:6060]
        PROD_SDLC[Azure SDLC<br/>legend-sdlc.azure-legend.com:7070]
        PROD_STUDIO[Azure Studio<br/>legend-studio.azure-legend.com:9000]
    end
    
    DEV_API --> DEV_ENGINE
    DEV_API --> DEV_SDLC
    
    PROD_API --> PROD_ENGINE
    PROD_API --> PROD_SDLC
    PROD_API --> PROD_STUDIO
```

## 📋 **Configuration Summary**

| Component | Port | Protocol | Purpose | Authentication |
|-----------|------|----------|---------|----------------|
| **Guardian Agent** | 8000 | HTTP | API Server | API Key (Bearer) |
| **Legend Engine** | 6060 | HTTP | Model Execution | Internal |
| **Legend SDLC** | 7070 | HTTP | Source Control | GitLab OAuth |
| **Legend Studio** | 9000 | HTTP | Web Interface | GitLab OAuth |
| **MongoDB** | 27017 | MongoDB | Data Storage | Internal |
| **Azure Ingress** | 80/443 | HTTP/HTTPS | External Access | Load Balancer |

This architecture provides a scalable, secure, and maintainable system for monitoring and managing the FINOS Legend platform through the Legend Guardian Agent.
