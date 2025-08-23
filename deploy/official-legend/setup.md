# Legend Guardian Workspace — Setup (Not the official FINOS Legend)

> This repository is **not configured to run the official FINOS Legend distribution directly**.  
> It contains a modular deployment system and local tooling tailored for the **Guardian Agent** workflows.
>
> For the upstream FINOS Legend docs and official deployment instructions, see: https://legend.finos.org

---

## What this repo is / isn't

- ✅ A **workspace** to run Legend components with Guardian Agent integration across local, Azure, and Kubernetes targets.
- ✅ A **modular deployment** tree under `deploy/` with environment-specific config and scripts.
- ❌ **Not** a drop‑in clone of the official FINOS Legend deployment. Don't expect `docker compose up` at the repo root to spin up the official stack.

See the full deployment breakdown in [`deploy/DEPLOYMENT_GUIDE.md`](../DEPLOYMENT_GUIDE.md).

---

## Prerequisites (local dev)

- Docker + Docker Compose
- Git (and a shell environment with `bash`)
- Optional (but recommended for HTTPS dev): `mkcert`
- A GitLab OAuth app if you want SSO locally (see [GitLab OAuth Setup](../GITLAB_OAUTH_SETUP.md))

---

## Quick start options

### Option A — Run all Legend services with Docker Compose

1.  **Configure your environment**

    Before running the services, you need to create a `.env` file from the provided template.

    ```bash
    # Navigate to the correct directory
    cd deploy/official-legend

    # Create the .env file
    cp .env.template .env
    ```

    Next, edit the `.env` file and provide the necessary values, especially for your GitLab OAuth application.

    **Note:** The `COMPOSE_PROJECT_NAME` in the `.env` file must consist only of lowercase alphanumeric characters, hyphens, and underscores.

2.  **Start the services**

    Now you can start all the services using Docker Compose.

    ```bash
    # Start all services in the background
    docker compose up -d
    ```

### Option B — Run specific services only

If you only need to run a subset of the services, you can use the `--profile` flag with the `docker compose up` command.

```bash
# Example: Run only the studio and engine services
docker compose --profile studio --profile engine up -d
```

### Available Profiles
- `setup` - Runs configuration setup
- `engine` - Legend Engine service
- `sdlc` - Legend SDLC service  
- `depot` - Legend Depot Store service
- `query` - Legend Query service
- `studio` - Legend Studio UI
- `postgres` - PostgreSQL database

---

## Reverse Proxy & Dev Domain Setup

This repository supports running all Legend services under a **single development domain** (`dev.atheryon.ai`) using a reverse proxy (Traefik). This setup:

- Avoids CORS and cookie issues when developing locally.
- Mirrors how services are deployed in production (single domain, path-based routing).

### Steps for Developers

1. **Make the dev domain resolve to your PC**

   Ensure that `dev.atheryon.ai` resolves to the IP address of your development machine. For local-only use, add to your hosts file:

   ```
   127.0.0.1 dev.atheryon.ai
   ```

   Alternatively, if you control the DNS for `atheryon.ai`, you can configure a DNS record (A or CNAME) to point `dev.atheryon.ai` to your PC's IP (e.g. on your LAN or public IP).

2. **Start the reverse proxy**

   The reverse proxy is automatically included via the Docker Compose override file:
   ```bash
   cd deploy/official-legend
   docker compose up   # Automatically uses docker-compose.override.yml
   ```
   The `reverse-proxy` service is defined in [`docker-compose.override.yml`](./docker-compose.override.yml). Docker Compose automatically applies this override file when you run `docker compose up` in this directory, starting Traefik alongside the Legend services.

3. **Access services via the dev domain**

   Once running, you can access each service at the following paths:
   - [http://dev.atheryon.ai/studio](http://dev.atheryon.ai/studio)
   - [http://dev.atheryon.ai/sdlc/api/info](http://dev.atheryon.ai/sdlc/api/info)
   - [http://dev.atheryon.ai/engine/api/server/version](http://dev.atheryon.ai/engine/api/server/version)
   - [http://dev.atheryon.ai/depot/depot/api/info](http://dev.atheryon.ai/depot/depot/api/info)

### Studio configuration

When running behind the reverse proxy, **Legend Studio** should be configured to use _relative URLs_ for backend APIs:
```
/sdlc/api
/engine/api
/depot/depot/api
```
This ensures all browser requests are routed through the proxy and avoid cross-origin issues.

### Optional: Local HTTPS (TLS)

For local HTTPS, you can use [`mkcert`](https://github.com/FiloSottile/mkcert) to generate trusted certificates for `dev.atheryon.ai`. This is recommended for testing SSO or secure cookies.

---

### Network Flow Diagram

The diagram below shows how all requests flow through the reverse proxy at `dev.atheryon.ai` and are routed to the appropriate Legend service based on the URL path.

```mermaid
flowchart LR
    Browser[Browser<br/>(http://dev.atheryon.ai)]
    Traefik[Traefik<br/>(reverse-proxy)]
    Studio[legend-studio:9000]
    SDLC[legend-sdlc:6100]
    Engine[legend-engine:6300]
    Depot[legend-depot:6200]

    Browser -->|HTTP request| Traefik
    Traefik -- "/studio" --> Studio
    Traefik -- "/sdlc" --> SDLC
    Traefik -- "/engine" --> Engine
    Traefik -- "/depot" --> Depot
```