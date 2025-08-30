
# Runbook

This document provides instructions for operating the Legend Guardian Agent.

## Quick Start

1.  Clone the repository.
2.  Run `make dev` to start the application.
3.  The API will be available at `http://localhost:8000`.

## Health Checks

To check the health of the application and its dependencies, make a GET request to the `/health` endpoint:

```bash
curl http://localhost:8000/health
```

## Environment Variables

The application is configured using environment variables. See the `.env.example` file for a list of all available variables.

## Common Errors

-   **403 Forbidden**: This error indicates that the API key is missing or invalid. Make sure you are providing a valid API key in the `X-API-Key` header.
