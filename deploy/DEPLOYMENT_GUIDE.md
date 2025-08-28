# Legend Platform Deployment Guide

## Overview

This repository provides standard, out-of-the-box deployments for the FINOS Legend platform. The goal is to offer clean, maintainable, and official setups.

**NOTE:** These deployments are intended to be used as-is to reflect the official open-source distribution. They should not be heavily customized directly. For custom setups, please fork this repository.

This guide provides a high-level overview of the available deployment methods. Please refer to the specific README file within each deployment directory for detailed instructions.

---

## 1. Docker Deployment (Official FINOS)

A comprehensive, full-stack deployment using the official FINOS Legend Docker Compose setup. This method is ideal for local development and evaluation. It uses a profile-based system to launch various combinations of Legend services.

- **Technology:** Docker, Docker Compose
- **Configuration:** Uses `.env` file and `secrets.env` for GitLab OAuth
- **Script:** Use `run-legend.sh` for easy deployment management
- **Details:** [**Docker Deployment README**](./docker-finos-official/README_DOCKER.md)

---

## 2. Kubernetes Deployment

A set of manifests and scripts for deploying the Legend platform to a Kubernetes cluster. This method is suitable for more scalable or production-like environments.

- **Technology:** Kubernetes, Kubectl, Kustomize
- **Configuration:** Uses `.yaml` manifests with Kustomize for customization
- **Details:** [**Kubernetes Deployment README**](./k8s/README.md)
- **Azure Deployment:** [**Azure AKS Deployment**](./k8s-azure/) with automated scripts

---

## Additional Deployment Options

### Docker Local Development

A simplified Docker Compose setup for quick local development:
- **Location:** `./docker-local/`
- **Script:** `start.sh` for easy startup
- **Use Case:** Quick testing and development

### Environment-Specific Overrides

- **Docker Configs:** `./docker-config-overrides/` - Configuration files for Docker deployments
- **K8s Overrides:** `./k8s-overrides/` - Environment-specific Kubernetes customizations

---

## Prerequisites

### For Docker Deployment:
- Docker and Docker Compose installed
- GitLab OAuth credentials configured (see [GitLab OAuth Setup](./GITLAB_OAUTH_SETUP.md))
- Environment variables configured in `secrets.env`

### For Kubernetes Deployment:
- Kubernetes cluster (1.19+)
- kubectl configured
- Kustomize (optional, for customization)
