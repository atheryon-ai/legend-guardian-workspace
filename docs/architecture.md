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
        ENGINE[Legend Engine<br/>Port 6300]
        SDLC[Legend SDLC<br/>Ports 6100/6101]
        STUDIO[Legend Studio<br/>Port 80<br/>134.33.215.176]
        STUDIO_NEW[Legend Studio New<br/>Port 80<br/>172.171.90.17]
        STUDIO_PROD[Legend Studio Prod<br/>Port 80<br/>52.186.106.13]
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
    CLIENTS -->|HTTP/6300| ENGINE
    CLIENTS -->|HTTP/6100/6101| SDLC
    CLIENTS -->|HTTP/80| STUDIO
    CLIENTS -->|HTTP/80| STUDIO_NEW
    CLIENTS -->|HTTP/80| STUDIO_PROD
  
    %% Database connections
    ENGINE -->|MongoDB| MONGO
    SDLC -->|MongoDB| MONGO
  
    %% Network flow
    INGRESS -->|HTTPS/443| LOADBAL
    LOADBAL -->|HTTP/80| API
    LOADBAL -->|HTTP/80| STUDIO
    LOADBAL -->|HTTP/80| STUDIO_NEW
    LOADBAL -->|HTTP/80| STUDIO_PROD
    LOADBAL -->|HTTP/80| ENGINE
    LOADBAL -->|HTTP/80| SDLC
  
    %% Security
    FIREWALL -->|Port Rules| INGRESS
    FIREWALL -->|Port Rules| LOADBAL
```

## 🚀 **Current Azure Deployment Reality**

### **Active Azure Infrastructure**

```
rs-finos-legend Resource Group
├── aks-legend (AKS Cluster)
│   ├── 3 nodes (Standard_D2_v3)
│   ├── Kubernetes 1.32
│   └── East US region
├── vnet-legend (Virtual Network)
├── nsg-legend (Network Security Group)
├── acrlegend10a89eda (Container Registry) ✅ ACTIVE
└── Monitoring Components
    ├── Prometheus rule groups
    ├── Data collection rules
    └── Metrics endpoints
```

### **Detailed Infrastructure Components**


| Azure Resource      | Type                     | Status    | Purpose                                                 |
| :-------------------- | -------------------------- | ----------- | --------------------------------------------------------- |
| `aks-legend`        | Azure Kubernetes Service | ✅ Active | Production Kubernetes cluster (3 nodes, Standard_D2_v3) |
| `vnet-legend`       | Virtual Network          | ✅ Active | Network isolation for AKS cluster                       |
| `nsg-legend`        | Network Security Group   | ✅ Active | Firewall rules for network security                     |
| `acrlegend10a89eda` | Container Registry       | ✅ Active | **Primary container registry** (actually used)          |
|                     |                          |           |                                                         |

### **Monitoring Components (Prometheus)**


| Component                                        | Purpose                 | Status    |
| -------------------------------------------------- | ------------------------- | ----------- |
| `KubernetesRecordingRulesRuleGroup - aks-legend` | AKS monitoring rules    | ✅ Active |
| `NodeRecordingRulesRuleGroup - aks-legend`       | Node metrics collection | ✅ Active |
| `UXRecordingRulesRuleGroup - aks-legend`         | User experience metrics | ✅ Active |
| `MSCI-eastus-aks-legend`                         | Data collection rules   | ✅ Active |
| `MSProm-eastus-aks-legend`                       | Prometheus endpoints    | ✅ Active |

### **Actually Running Services**

#### **Legend Namespace (Main)**

```
┌─────────────────────────────────────────────────────────────┐
│                    Legend Namespace                        │
├─────────────────────────────────────────────────────────────┤
│ Service           │ Port │ Type        │ External IP        │
├─────────────────────────────────────────────────────────────┤
│ legend-engine     │ 6300 │ ClusterIP   │ None               │
│ legend-sdlc       │6100/1│ ClusterIP   │ None               │
│ legend-studio     │  80  │ LoadBalancer│ 134.33.215.176     │
│ legend-studio-new │  80  │ LoadBalancer│ 172.171.90.17      │
│ mongodb           │27017 │ ClusterIP   │ None               │
└─────────────────────────────────────────────────────────────┘
```

#### **Legend-Prod Namespace**

```
┌─────────────────────────────────────────────────────────────┐
│                  Legend-Prod Namespace                     │
├─────────────────────────────────────────────────────────────┤
│ Service           │ Port │ Type        │ External IP        │
├─────────────────────────────────────────────────────────────┤
│ legend-studio     │  80  │ LoadBalancer│ 52.186.106.13      │
└─────────────────────────────────────────────────────────────┘
```

### **Detailed Service Status**


| Service              | Type         | Port      | External IP    | Status     | Image                               |
| ---------------------- | -------------- | ----------- | ---------------- | ------------ | ------------------------------------- |
| `legend-engine`      | ClusterIP    | 6300      | None           | ✅ Running | `finos/legend-engine-server:4.25.1` |
| `legend-sdlc`        | ClusterIP    | 6100/6101 | None           | ✅ Running | `finos/legend-sdlc:latest`          |
| `legend-studio`      | LoadBalancer | 80        | 134.33.215.176 | ✅ Running | `finos/legend-studio:4.9.0`         |
| `legend-studio-new`  | LoadBalancer | 80        | 172.171.90.17  | ✅ Running | `finos/legend-studio:4.9.0`         |
| `mongodb`            | ClusterIP    | 27017     | None           | ✅ Running | `mongo:6.0`                         |
| `legend-studio-prod` | LoadBalancer | 80        | 52.186.106.13  | ✅ Running | `finos/legend-studio:3.0.0`         |

### **Missing Components**


| Component              | Expected    | Reality        | Notes                |
| ------------------------ | ------------- | ---------------- | ---------------------- |
| **Guardian Agent**     | Port 8000   | ❌ Not Running | No pods found        |
| **Ingress Controller** | Port 80/443 | ❌ Not Found   | No ingress resources |

### **Container Images (Actual)**


| Service              | Image                               | Source     | Status     |
| ---------------------- | ------------------------------------- | ------------ | ------------ |
| `legend-engine`      | `finos/legend-engine-server:4.25.1` | Docker Hub | ✅ Running |
| `legend-sdlc`        | `finos/legend-sdlc:latest`          | Docker Hub | ✅ Running |
| `legend-studio`      | `finos/legend-studio:4.9.0`         | Docker Hub | ✅ Running |
| `legend-studio-new`  | `finos/legend-studio:4.9.0`         | Docker Hub | ✅ Running |
| `legend-studio-prod` | `finos/legend-studio:3.0.0`         | Docker Hub | ✅ Running |
| `mongodb`            | `mongo:6.0`                         | Docker Hub | ✅ Running |

### **Current Network Flow (Reality)**

```
Internet
    ↓
Azure Load Balancer (Port 80 only)
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    AKS Cluster                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Legend Namespace                       │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │   Engine    │ │    SDLC     │ │   Studio    │   │   │
│  │  │   Port      │ │   Ports     │ │   Port 80   │   │   │
│  │  │   6300      │ │  6100/6101  │ │  Ext IP     │   │   │
│  │  │ (Internal)  │ │ (Internal)  │ │134.33.215.176│   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │ Studio-New  │ │  MongoDB    │ │             │   │   │
│  │  │ Port 80     │ │ Port 27017  │ │             │   │   │
│  │  │ Ext IP      │ │ (Internal)  │ │             │   │   │
│  │  │172.171.90.17│ │             │ │             │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Legend-Prod Namespace                   │   │
│  │  ┌─────────────┐                                   │   │
│  │  │   Studio    │                                   │   │
│  │  │ Port 80     │                                   │   │
│  │  │ Ext IP      │                                   │   │
│  │  │52.186.106.13│                                   │   │
│  │  └─────────────┘                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Deployment Status Summary**


| Component          | Actual Port    | Expected Port | Status        | Action      |
| -------------------- | ---------------- | --------------- | --------------- | ------------- |
| **Legend Engine**  | 6300           | 6300          | ✅**MATCHES** | None needed |
| **Legend SDLC**    | 6100/6101      | 6100/6101     | ✅**MATCHES** | None needed |
| **Legend Studio**  | 80             | 80            | ✅**MATCHES** | None needed |
| **MongoDB**        | 27017          | 27017         | ✅**MATCHES** | None needed |
| **Guardian Agent** | Not Running    | 8000          | ❌ Missing    | Deploy      |
| **Ingress**        | Not Configured | 80/443        | ❌ Missing    | Install     |

**Overall Progress: 67% Complete** (4/6 components deployed and configured)

### **Immediate Actions Required**

#### **✅ COMPLETED**

1. **Fix Port Mismatches** - Architecture diagrams updated to match reality
2. **Clean Up Duplicates** - Unused container registry removed
3. **Infrastructure Audit** - Current deployment state documented

#### **🔄 STILL NEEDED**

4. **Deploy Guardian Agent**:

   - Currently missing - needs deployment
   - `kubectl apply -f k8s/legend-guardian-agent.yaml -n legend`
5. **Add Ingress Controller**:

   - Install NGINX ingress controller
   - Configure HTTPS/443 routing
6. **Add Load Balancer HTTPS Support**:

   - Configure port 443 for HTTPS
   - Set up SSL certificates

## 🔧 **Recommended Actions & Progress Tracking**

### **✅ COMPLETED**

1. **Update Architecture Diagrams** to reflect actual ports:

   - ✅ Engine: 6300 (updated)
   - ✅ SDLC: 6100/6101 (updated)
   - ✅ Studio: 80 (updated)
2. **Remove Duplicate Container Registry**:

   - ✅ Deleted `acrlegend23821aae` (completed)
3. **Port Standardization**:

   - ✅ All port mismatches resolved
   - ✅ Architecture diagrams now match reality
4. **Infrastructure Audit**:

   - ✅ Documented all running services
   - ✅ Identified missing components

### **🔄 STILL NEEDED**

5. **Deploy Guardian Agent**:

   - Currently missing from architecture
   - Needed for automation features
6. **Add Ingress Controller**:

   - Configure HTTPS/443
   - Set up proper routing rules
7. **Add Load Balancer HTTPS Support**:

   - Configure port 443 for HTTPS
   - Set up SSL certificates

## 🎯 **Next Steps Progress**

1. **✅ COMPLETED**: Document all running services and their actual configurations
2. **✅ COMPLETED**: Modify architecture diagrams to match reality
3. **🔄 NEEDED**: Deploy Guardian Agent (missing automation component)
4. **✅ COMPLETED**: Port standardization (diagrams now match reality)
5. **🔄 NEEDED**: Add Ingress Controller (proper external routing)
6. **✅ COMPLETED**: Remove unused resources (duplicate ACR)

**Progress: 4/6 components aligned** ✅
**Remaining: Guardian Agent deployment and Ingress controller setup**

### **Current Architecture Reality (Simplified View)**

```
Internet
    ↓
Azure Load Balancer (Port 80 only)
    ↓
┌─────────────────────────────────────┐
│           AKS Cluster              │
│  ┌─────────────────────────────┐   │
│  │       Legend Namespace      │   │
│  │  ┌─────────┐ ┌─────────┐   │   │
│  │  │ Engine  │ │  SDLC   │   │   │
│  │  │ Port    │ │ Ports   │   │   │
│  │  │ 6300    │ │6100/6101│   │   │
│  │  └─────────┘ └─────────┘   │   │
│  │  ┌─────────┐ ┌─────────┐   │   │
│  │  │ Studio  │ │ MongoDB │   │   │
│  │  │ Port 80 │ │ Port    │   │   │
│  │  │ Ext IP  │ │ 27017   │   │   │
│  │  └─────────┘ └─────────┘   │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │     Legend-Prod Namespace   │   │
│  │  ┌─────────┐               │   │
│  │  │ Studio  │               │   │
│  │  │ Port 80 │               │   │
│  │  │ Ext IP  │               │   │
│  │  └─────────┘               │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
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
        ENGINE_CLIENT[Engine Client<br/>HTTP/6300]
        SDLC_CLIENT[SDLC Client<br/>HTTP/6100/6101]
        STUDIO_CLIENT[Studio Client<br/>HTTP/80]
    end
  
    subgraph "Data Layer"
        MEMORY[Memory System<br/>Event Store]
        CONFIG[Configuration<br/>Environment]
        LOGS[Logging System]
    end
  
    subgraph "External Services"
        LEGEND_ENGINE[Legend Engine<br/>Port 6300]
        LEGEND_SDLC[Legend SDLC<br/>Ports 6100/6101]
        LEGEND_STUDIO[Legend Studio<br/>Port 80]
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
    ENGINE_CLIENT -->|HTTP/6300| LEGEND_ENGINE
    SDLC_CLIENT -->|HTTP/6100/6101| LEGEND_SDLC
    STUDIO_CLIENT -->|HTTP/80| LEGEND_STUDIO
  
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
            INGRESS[Azure Load Balancer<br/>Port 80 Only]
        end
      
        subgraph "Legend Guardian Agent Namespace"
            GUARDIAN_POD[Guardian Agent Pod<br/>Port 8000]
            GUARDIAN_SVC[Guardian Agent Service<br/>Port 8000]
        end
      
        subgraph "Legend Platform Namespace"
            STUDIO_POD[Legend Studio Pod<br/>Port 80<br/>134.33.215.176]
            STUDIO_SVC[Legend Studio Service<br/>Port 80]
          
            STUDIO_NEW_POD[Legend Studio New Pod<br/>Port 80<br/>172.171.90.17]
            STUDIO_NEW_SVC[Legend Studio New Service<br/>Port 80]
          
            ENGINE_POD[Legend Engine Pod<br/>Port 6300]
            ENGINE_SVC[Legend Engine Service<br/>Port 6300]
          
            SDLC_POD[Legend SDLC Pod<br/>Ports 6100/6101]
            SDLC_SVC[Legend SDLC Service<br/>Ports 6100/6101]
        end
      
        subgraph "Legend-Prod Namespace"
            STUDIO_PROD_POD[Legend Studio Prod Pod<br/>Port 80<br/>52.186.106.13]
            STUDIO_PROD_SVC[Legend Studio Prod Service<br/>Port 80]
        end
      
        subgraph "Database Namespace"
            MONGO_POD[MongoDB Pod<br/>Port 27017]
            MONGO_SVC[MongoDB Service<br/>Port 27017]
        end
    end
  
    %% External connections
    USERS -->|HTTP/80| INGRESS
    GITLAB -->|OAuth/80| INGRESS
  
    %% Load Balancer routing
    INGRESS -->|HTTP/80| STUDIO_SVC
    INGRESS -->|HTTP/80| STUDIO_NEW_SVC
    INGRESS -->|HTTP/80| STUDIO_PROD_SVC
    %% Note: Guardian Agent not yet deployed
    %% Note: Engine and SDLC are internal only
  
    %% Service to Pod routing
    GUARDIAN_SVC -->|Internal| GUARDIAN_POD
    STUDIO_SVC -->|Internal| STUDIO_POD
    STUDIO_NEW_SVC -->|Internal| STUDIO_NEW_POD
    STUDIO_PROD_SVC -->|Internal| STUDIO_PROD_POD
    ENGINE_SVC -->|Internal| ENGINE_POD
    SDLC_SVC -->|Internal| SDLC_POD
  
    %% Internal service communication
    GUARDIAN_POD -->|HTTP/6300| ENGINE_POD
    GUARDIAN_POD -->|HTTP/6100/6101| SDLC_POD
    GUARDIAN_POD -->|HTTP/80| STUDIO_POD
    GUARDIAN_POD -->|HTTP/80| STUDIO_NEW_POD
    GUARDIAN_POD -->|HTTP/80| STUDIO_PROD_POD
  
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
- **Status**: ❌ **Not Deployed** - Needs `kubectl apply -f k8s/legend-guardian-agent.yaml -n legend`

### **Legend Engine**

- **Port**: 6300
- **Protocol**: HTTP
- **Purpose**: Model execution and validation
- **Database**: MongoDB (Port 27017)

### **Legend SDLC**

- **Ports**: 6100, 6101
- **Protocol**: HTTP
- **Purpose**: Source control and lifecycle management
- **Database**: MongoDB (Port 27017)

### **Legend Studio Services**


| Service                | Port | Protocol | External IP    | Purpose                       | Authentication |
| ------------------------ | ------ | ---------- | ---------------- | ------------------------------- | ---------------- |
| **Legend Studio**      | 80   | HTTP     | 134.33.215.176 | Web-based modeling interface  | GitLab OAuth   |
| **Legend Studio New**  | 80   | HTTP     | 172.171.90.17  | Updated modeling interface    | GitLab OAuth   |
| **Legend Studio Prod** | 80   | HTTP     | 52.186.106.13  | Production modeling interface | GitLab OAuth   |

### **MongoDB**

- **Port**: 27017
- **Protocol**: MongoDB Wire Protocol
- **Purpose**: Data persistence for all Legend services

### **Azure Ingress**

- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Protocol**: HTTP/HTTPS
- **Purpose**: External access and load balancing
- **Status**: ⚠️ **HTTP Only** - Port 80 configured, HTTPS/443 not yet set up

## 🔄 **Deployment Architecture**

```mermaid
graph LR
    subgraph "Development"
        DEV_API[Local API<br/>localhost:8000]
        DEV_ENGINE[Local Engine<br/>localhost:6300]
        DEV_SDLC[Local SDLC<br/>localhost:6100]
    end
  
    subgraph "Production (Azure AKS)"
        PROD_API[Azure API<br/>legend-guardian.azure-legend.com:8000]
        PROD_ENGINE[Azure Engine<br/>legend-engine.azure-legend.com:6300]
        PROD_SDLC[Azure SDLC<br/>legend-sdlc.azure-legend.com:6100]
        PROD_STUDIO[Azure Studio<br/>134.33.215.176:80]
        PROD_STUDIO_NEW[Azure Studio New<br/>172.171.90.17:80]
        PROD_STUDIO_PROD[Azure Studio Prod<br/>52.186.106.13:80]
    end
  
    DEV_API --> DEV_ENGINE
    DEV_API --> DEV_SDLC
  
    PROD_API --> PROD_ENGINE
    PROD_API --> PROD_SDLC
    PROD_API --> PROD_STUDIO
    PROD_API --> PROD_STUDIO_NEW
    PROD_API --> PROD_STUDIO_PROD
```

## 📋 **Configuration Summary**

| Component | Port | Protocol | External IP | Purpose | Authentication | Status |
|-----------|------|----------|-------------|---------|----------------|
| **Guardian Agent** | 8000 | HTTP | None | API Server | API Key (Bearer) | ❌ Not Deployed |
| **Legend Engine** | 6300 | HTTP | None | Model Execution | Internal | ✅ Running |
| **Legend SDLC** | 6100/6101 | HTTP | None | Source Control | GitLab OAuth | ✅ Running |
| **Legend Studio** | 80 | HTTP | 134.33.215.176 | Web Interface | GitLab OAuth | ✅ Running |
| **Legend Studio New** | 80 | HTTP | 172.171.90.17 | Web Interface | GitLab OAuth | ✅ Running |
| **Legend Studio Prod** | 80 | HTTP | 52.186.106.13 | Web Interface | GitLab OAuth | ✅ Running |
| **MongoDB** | 27017 | MongoDB | None | Data Storage | Internal | ✅ Running |
| **Azure Ingress** | 80/443 | HTTP/HTTPS | Load Balancer | External Access | Load Balancer | ⚠️ HTTP Only |

## 🌐 **External Access URLs**

### **Legend Studio Services**

- **Main Studio**: http://134.33.215.176:80
- **New Studio**: http://172.171.90.17:80
- **Production Studio**: http://52.186.106.13:80

### **Resource Groups**

- **Main Resources**: `rs-finos-legend`
- **AKS-Managed Resources**: `mc_rs-finos-legend_aks-legend_eastus`

This architecture provides a scalable, secure, and maintainable system for monitoring and managing the FINOS Legend platform through the Legend Guardian Agent.
