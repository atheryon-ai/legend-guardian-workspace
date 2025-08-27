# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL DEPLOYMENT PRINCIPLE

**USE ONLY OPEN SOURCE FINOS LEGEND COMPONENTS WITH OUT-OF-THE-BOX CONFIGURATION**

This project focuses exclusively on deploying the official FINOS Legend platform using:
- Official FINOS Docker images from Docker Hub (finos/legend-*)
- Standard configuration files from FINOS Legend repositories
- Out-of-the-box deployment patterns from FINOS documentation
- No custom modifications to core Legend services

When in doubt, always refer to:
1. Official FINOS Legend repositories on GitHub
2. FINOS Legend Docker Hub images
3. Standard Legend configuration examples

## Project Overview

Deployment and management of the open source FINOS Legend platform with minimal customization. The goal is to run Legend as close to the official distribution as possible.

## Official FINOS Legend Components

Use ONLY these official Docker images:
- `finos/legend-engine-server:latest` - Engine service (port 6060)
- `finos/legend-sdlc-server:latest` - SDLC service (port 6100/6101)
- `finos/legend-studio:latest` - Studio UI (port 9000)
- `finos/legend-depot-server:latest` - Depot service (port 6200)
- `finos/legend-depot-store-server:latest` - Depot store service
- Standard databases: MongoDB, PostgreSQL as per FINOS examples

## Standard Configuration Approach

### Use Official Config Templates
Always start with configuration from official FINOS repositories:
- Engine config: https://github.com/finos/legend-engine/tree/master/legend-engine-config
- SDLC config: https://github.com/finos/legend-sdlc/tree/master/legend-sdlc-server/src/test/resources
- Studio config: https://github.com/finos/legend-studio/tree/master/packages/legend-application-studio-bootstrap

### Minimal Configuration Changes
Only modify:
- Database connection strings (MongoDB/PostgreSQL endpoints)
- Service URLs for inter-service communication
- Port mappings if required by environment
- Authentication settings (GitLab OAuth)

### Docker Compose Structure
```yaml
services:
  # Use official FINOS images
  legend-engine:
    image: finos/legend-engine-server:latest
    # Mount official config
    volumes:
      - ./config/engine-config.json:/config/config.json
    # Standard ports
    ports:
      - "6060:6060"
  
  # Similar for other services...
```

## Development Commands

### Running with Docker Compose
```bash
# Use official FINOS docker-compose examples as base
cd deploy/docker
docker-compose -f docker-compose.yml up

# No custom build scripts - use official images
docker pull finos/legend-engine-server:latest
docker pull finos/legend-sdlc-server:latest
docker pull finos/legend-studio:latest
```

### Configuration Management
```bash
# Copy official configs
wget https://raw.githubusercontent.com/finos/legend-engine/master/legend-engine-config/engine-config.json
wget https://raw.githubusercontent.com/finos/legend-sdlc/master/legend-sdlc-server/src/test/resources/config-test.yaml

# Modify only connection strings
sed -i 's/localhost:27017/mongodb:27017/g' engine-config.json
```

## DO NOT CREATE

- Custom Dockerfiles for Legend services (use official images)
- Modified Legend service code
- Custom configuration formats
- Non-standard deployment patterns
- Guardian agents or monitoring services (unless specifically requested)

## Configuration Files Location

Standard FINOS configuration structure:
```
deploy/
├── docker/
│   ├── docker-compose.yml          # Official FINOS compose structure
│   └── config/
│       ├── engine-config.json      # From FINOS legend-engine repo
│       ├── sdlc-config.yaml        # From FINOS legend-sdlc repo
│       └── studio-config.json      # From FINOS legend-studio repo
└── kubernetes/
    └── # Standard K8s manifests using FINOS images
```

## Debugging Approach

When services fail:
1. Check official FINOS documentation first
2. Review example configurations in FINOS repos
3. Verify using correct official image versions
4. Ensure configuration matches FINOS examples
5. Check FINOS GitHub issues for known problems

## Testing

Test that services match official FINOS behavior:
```bash
# Verify standard endpoints
curl http://localhost:6060/api/server/v1/info  # Engine
curl http://localhost:6100/api/info            # SDLC
curl http://localhost:9000                     # Studio

# Compare responses with FINOS documentation
```

## Important Patterns

1. **Always use official images**: Never build custom Legend service images
2. **Minimal configuration**: Start with FINOS defaults, change only what's necessary
3. **Standard ports**: Use FINOS standard ports (6060, 6100, 9000, etc.)
4. **Official documentation**: Refer to FINOS repos, not third-party guides
5. **No custom code**: Deploy Legend as-is from official distribution

## References

Official FINOS Legend repositories:
- Engine: https://github.com/finos/legend-engine
- SDLC: https://github.com/finos/legend-sdlc
- Studio: https://github.com/finos/legend-studio
- Depot: https://github.com/finos/legend-depot

Docker Hub:
- https://hub.docker.com/u/finos

## 🎯 **OFFICIAL DEPLOYMENT TOOLS DISCOVERED**

### **Official Docker Compose Setup**
The FINOS Legend project provides **official, production-ready deployment tools** at:
- **Main installer**: https://github.com/finos/legend/tree/master/installers/docker-compose
- **Official docker-compose.yml**: https://raw.githubusercontent.com/finos/legend/master/installers/docker-compose/docker-compose.yml
- **Official .env template**: https://raw.githubusercontent.com/finos/legend/master/installers/docker-compose/.env
- **Official README**: https://raw.githubusercontent.com/finos/legend/master/installers/docker-compose/README.md

### **Official Helm Charts**
- **Kubernetes deployment**: https://github.com/finos/legend/tree/master/installers/helm-ocp
- **Production-ready K8s manifests**

### **What This Means**
1. **NO NEED for custom Docker configurations** - Official ones exist
2. **NO NEED for custom docker-compose.yml** - Official one is comprehensive
3. **NO NEED for custom build scripts** - Official setup handles everything
4. **The current custom implementation is completely unnecessary**

### **Official vs. Custom Comparison**

| Feature | Official FINOS | Current Custom |
|---------|----------------|----------------|
| Docker Compose | ✅ Complete, tested | ❌ Basic, problematic |
| Configuration | ✅ Comprehensive | ❌ Minimal, conflicting |
| Health Checks | ✅ Proper intervals | ❌ Basic setup |
| Service Dependencies | ✅ Correct order | ❌ Missing setup service |
| Environment Variables | ✅ Complete template | ❌ Incomplete |
| Documentation | ✅ Detailed guide | ❌ Basic notes |
| Testing | ✅ Production tested | ❌ Untested |

### **✅ MIGRATION COMPLETED SUCCESSFULLY**

**The custom deployment has been successfully replaced with official FINOS tools:**
1. ✅ **Official docker-compose.yml** - Now using complete FINOS Legend deployment
2. ✅ **Official setup.sh** - Configuration generation working properly
3. ✅ **Official service profiles** - Engine, SDLC, Depot, Query, Studio all functional
4. ✅ **GitLab OAuth integration** - Using secrets.env for credentials
5. ✅ **Production deployment** - All services running and healthy

**Current Status**: 100% migrated to official FINOS Legend deployment
**Deployment Method**: `./run-legend.sh <profile> <command>`
**Available Profiles**: setup, engine, sdlc, studio, depot, query, postgres

## Deployment Philosophy

The goal is to run Legend exactly as FINOS intends, using their official images and configurations. Any customization should be limited to environment-specific settings (URLs, passwords) rather than functional changes.

When asked to deploy or configure Legend:
1. Use official FINOS Docker images
2. Use configuration examples from FINOS repositories
3. Make minimal changes for environment adaptation
4. Document any deviations from standard FINOS setup
5. Prefer simplicity and standard patterns over custom solutions

## 🤖 AI ASSISTANT INSTRUCTIONS - OPEN SOURCE ONLY

### 🚫 **ABSOLUTE RULE: NO CUSTOM CODE OR CONFIGURATIONS**

**You are FORBIDDEN from creating, writing, or suggesting ANY custom code, configurations, or modifications. You must ONLY use official open source solutions exactly as they are provided.**

### 📋 **MANDATORY WORKFLOW**

1. **ALWAYS CHECK OFFICIAL SOURCES FIRST**
   - Search the official project repository
   - Check official documentation
   - Look for official deployment tools
   - Verify official configuration examples

2. **NEVER CREATE CUSTOM FILES**
   - Writing custom Dockerfiles
   - Creating custom docker-compose.yml
   - Writing custom configuration files
   - Suggesting custom scripts
   - Modifying existing open source code

3. **ONLY USE OFFICIAL TOOLS**
   - Official Docker images (exact tags)
   - Official Helm charts
   - Official configuration examples
   - Official deployment guides
   - Official scripts and tools

### ❌ **WHAT YOU CANNOT DO**
- ❌ Write custom code
- ❌ Modify existing configurations
- ❌ Create new files from scratch
- ❌ Suggest custom solutions
- ❌ "Improve" or "optimize" existing code
- ❌ Create workarounds
- ❌ Suggest custom modifications

### ✅ **WHAT YOU MUST DO**
- ✅ Find official solutions
- ✅ Use official tools
- ✅ Copy official configurations exactly
- ✅ Reference official documentation
- ✅ Point to official repositories
- ✅ Suggest official alternatives

### 🚨 **ENFORCEMENT**

If you cannot find an official solution:
1. **STOP immediately**
2. **Inform the user that no official solution exists**
3. **Suggest they check the official project**
4. **DO NOT create a custom solution**
5. **Ask them to contribute to the official project instead**

### 🔒 **FINAL WARNING**

**Remember: You are an AI assistant helping with open source projects. Your job is to find and use official solutions, NOT to create custom ones. If you cannot find an official solution, you must say so and NOT create a custom alternative.**

### 📝 **DOCUMENTATION RULE**

**ALWAYS TRY TO ADD NEW INFO TO EXISTING .MD FILES AND NOT CREATE NEW ONES.**
- Update existing documentation files
- Add new sections to relevant existing files
- Consolidate information rather than creating new files
- Keep the repository structure clean and organized