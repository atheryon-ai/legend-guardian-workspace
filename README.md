# Atheryon FINOS Legend

A clean, focused deployment of the FINOS Legend platform using Docker.

## 🎯 What This Project Does

This project deploys a comprehensive, full-stack FINOS Legend platform using a profile-based Docker Compose setup. It allows you to run various combinations of services, from a core modeling environment to a full-featured stack with data model sharing and querying capabilities.

For a detailed list of services, see the [Docker README](deploy/docker/README_DOCKER.md).

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- A `.env` file configured in `deploy/docker/`. You can copy `deploy/docker/.env.example` to get started.

### 1. Run the One-Time Setup

Generate the necessary configurations for the services.

```bash
# From the repository root directory
docker-compose --profile setup -f deploy/docker/docker-compose.yml up --build
```

### 2. Launch the Services

Run the core stack for data modeling.

```bash
# From the repository root directory
docker-compose --profile studio -f deploy/docker/docker-compose.yml up -d --build
```
For more advanced options, including running the full stack, see the detailed instructions in the [Docker README](deploy/docker/README_DOCKER.md).

## 📁 Project Structure

```
atheryon-finos-legend/
├── deploy/docker/
│   ├── .env.example         # Example environment configuration
│   ├── docker-compose.yml   # Main deployment file for the full stack
│   ├── setup.sh             # Script for the setup container
│   └── README_DOCKER.md     # Detailed Docker-specific documentation
├── docs/
└── ...
```

## 🔧 Configuration

The deployment is configured using the `.env` file in the `deploy/docker/` directory. See the [Docker README](deploy/docker/README_DOCKER.md) for more details.

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
