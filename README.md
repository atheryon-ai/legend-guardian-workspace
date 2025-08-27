# Atheryon FINOS Legend

A clean, focused deployment of the FINOS Legend platform using Docker.

## 🎯 What This Project Does

This project deploys a comprehensive, full-stack FINOS Legend platform using a profile-based Docker Compose setup. It allows you to run various combinations of services, from a core modeling environment to a full-featured stack with data model sharing and querying capabilities.

For a detailed list of services, see the [Docker README](deploy/docker/README_DOCKER.md).

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- GitLab OAuth credentials (see [GitLab OAuth Setup](deploy/GITLAB_OAUTH_SETUP.md))
- Environment variables configured (see [secrets.env](secrets.example))

### 1. Run the One-Time Setup

Generate the necessary configurations for the services.

```bash
# From the deploy/docker directory
./run-legend.sh setup up
```

### 2. Launch the Services

Run the core stack for data modeling.

```bash
# From the deploy/docker directory
./run-legend.sh studio up -d
```

For more advanced options, including running the full stack, see the detailed instructions in the [Docker README](deploy/docker/README_DOCKER.md).

## 📁 Project Structure

```
atheryon-finos-legend/
├── deploy/docker/
│   ├── run-legend.sh        # Main deployment script with secrets integration
│   ├── docker-compose.yml   # Official FINOS Legend deployment configuration
│   ├── setup.sh             # Configuration generation script
│   ├── .env                 # Environment configuration
│   └── README_DOCKER.md     # Detailed Docker-specific documentation
├── secrets.env              # Production secrets (not committed)
├── secrets.example          # Example secrets configuration
├── docs/                    # Architecture and deployment documentation
└── ...
```

## 🔧 Configuration

The deployment is configured using:
- **Environment variables** in `secrets.env` (GitLab OAuth, database connections)
- **Docker configuration** in `deploy/docker/.env` (service ports, versions)
- **Official FINOS Legend** docker-compose.yml with profile-based deployment

See the [Docker README](deploy/docker/README_DOCKER.md) and [GitLab OAuth Setup](deploy/GITLAB_OAUTH_SETUP.md) for detailed configuration instructions.

## 📚 Documentation

- [Docker Setup Details](deploy/docker/README_DOCKER.md)
- [Architecture](docs/architecture.md)

## 🤖 AI Assistant Instructions

**⚠️ IMPORTANT: All AI assistants working on this project MUST follow the instructions in [CLAUDE.md](CLAUDE.md).**

**Key Rules:**
- **NO CUSTOM CODE OR CONFIGURATIONS** - ONLY USE OFFICIAL OPEN SOURCE SOLUTIONS
- **NO NEW .MD FILES** - ALWAYS ADD NEW INFO TO EXISTING FILES
- **UPDATE EXISTING DOCUMENTATION** - KEEP REPOSITORY STRUCTURE CLEAN

## 🤝 Contributing

This project focuses solely on Legend platform deployment. For Legend platform development, see [FINOS Legend](https://github.com/finos/legend).
