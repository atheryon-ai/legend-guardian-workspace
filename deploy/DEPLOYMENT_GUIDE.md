# Legend Platform Deployment Guide

## Overview

This repository provides standard, out-of-the-box deployments for the FINOS Legend platform. The goal is to offer clean, maintainable, and official setups.

**NOTE:** These deployments are intended to be used as-is to reflect the official open-source distribution. They should not be heavily customized directly. For custom setups, please fork this repository.

This guide provides a high-level overview of the available deployment methods. Please refer to the specific README file within each deployment directory for detailed instructions.

---

## 1. Docker Deployment

A comprehensive, full-stack deployment using Docker Compose. This method is ideal for local development and evaluation. It uses a profile-based system to launch various combinations of Legend services.

- **Technology:** Docker, Docker Compose
- **Configuration:** Uses a `.env` file for environment variables.
- **Details:** [**Docker Deployment README**](./docker/README_DOCKER.md)

---

## 2. Kubernetes Deployment

A set of manifests and scripts for deploying the Legend platform to a Kubernetes cluster. This method is suitable for more scalable or production-like environments.

- **Technology:** Kubernetes, Kubectl
- **Configuration:** Uses `.yaml` manifests and environment-specific scripts.
- **Details:** [**Kubernetes Deployment README**](./kubernetes/README.md)
