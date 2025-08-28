# Atheryon FINOS Legend

A clean, focused deployment of the FINOS Legend platform using Docker.

## 🎯 What This Project Does

This project deploys a comprehensive, full-stack FINOS Legend platform using a profile-based Docker Compose setup. It allows you to run various combinations of services, from a core modeling environment to a full-featured stack with data model sharing and querying capabilities.

For a detailed list of services, see the [Docker README](deploy/docker-finos-official/README_DOCKER.md).

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- GitLab OAuth credentials (see [Secrets Guide](deploy/secrets/README.md))
- Environment variables configured (see [Setup Guide](deploy/secrets/README.md))

### 1. Run the One-Time Setup

Generate the necessary configurations for the services.

```bash
# From the deploy/docker-finos-official directory
./run-legend.sh setup up
```

### 2. Launch the Services

Run the core stack for data modeling.

```bash
# From the deploy/docker-finos-official directory
./run-legend.sh studio up -d
```

For more advanced options, including running the full stack, see the detailed instructions in the [Docker README](deploy/docker-finos-official/README_DOCKER.md).

## 📁 Project Structure

```
legend-guardian-workspace/
├── deploy/docker-finos-official/
│   ├── run-legend.sh        # Main deployment script with secrets integration
│   ├── docker-compose.yml   # Official FINOS Legend deployment configuration
│   ├── setup.sh             # Configuration generation script
│   ├── .env                 # Environment configuration
│   └── README_DOCKER.md     # Detailed Docker-specific documentation
├── .env.local               # Local environment secrets (not committed)
├── .env.example             # Example environment configuration
├── docs/                    # Architecture and deployment documentation
└── ...
```

## 🔧 Configuration

The deployment is configured using:
- **Environment variables** in `.env.local` (GitLab OAuth, database connections)
- **Docker configuration** in `deploy/docker-finos-official/.env` (service ports, versions)
- **Official FINOS Legend** docker-compose.yml with profile-based deployment

See the [Docker README](deploy/docker-finos-official/README_DOCKER.md) and [Secrets Guide](deploy/secrets/README.md) for detailed configuration instructions.

## 📚 Documentation

- [Docker Setup Details](deploy/docker-finos-official/README_DOCKER.md)
- [Secrets Management](deploy/secrets/README.md)
- [Architecture](docs/architecture.md)

## 🤖 AI Assistant Instructions

**⚠️ IMPORTANT: All AI assistants working on this project MUST follow the instructions in [CLAUDE.md](CLAUDE.md).**

**Key Rules:**
- **NO CUSTOM CODE OR CONFIGURATIONS** - ONLY USE OFFICIAL OPEN SOURCE SOLUTIONS
- **NO NEW .MD FILES** - ALWAYS ADD NEW INFO TO EXISTING FILES
- **UPDATE EXISTING DOCUMENTATION** - KEEP REPOSITORY STRUCTURE CLEAN

## 🤝 Contributing

This project focuses solely on Legend platform deployment. For Legend platform development, see [FINOS Legend](https://github.com/finos/legend).
