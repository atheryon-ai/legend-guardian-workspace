# Gemini Code Assistant Context

## Project Overview

This project is the **Legend Guardian Agent**, an intelligent agent designed to monitor and manage the FINOS Legend platform. It provides automated model validation, service generation, and deployment automation.

The application is a Python-based web service built with the **FastAPI** framework. It interacts with the **Legend Engine** and **Legend SDLC** services to perform its functions. The agent's core logic is encapsulated in the `LegendGuardianAgent` class, which is initialized and used by the FastAPI application.

The project is set up to be run locally for development and testing, and it can be deployed to a production environment using Docker and Kubernetes.

## Building and Running

### Local Development

1.  **Install Dependencies:**
    ```bash
    make install
    ```

2.  **Run the Application:**
    ```bash
    make run
    ```
    or for auto-reloading:
    ```bash
    make uvicorn
    ```

The API will be available at `http://localhost:8000`.

### Docker

1.  **Build the Docker Image:**
    ```bash
    docker build -t legend-guardian-agent .
    ```

2.  **Run the Docker Container:**
    ```bash
    docker run -p 8000:8000 legend-guardian-agent
    ```

### Docker Compose

1.  **Start all services:**
    ```bash
    docker-compose up -d
    ```

This will start the `legend-guardian-agent`, `legend-engine`, and `legend-sdlc` services.

## Testing

*   **Run all tests:**
    ```bash
    make test
    ```

*   **Run tests with coverage:**
    ```bash
    make coverage
    ```

## Development Conventions

*   **Code Formatting:** The project uses the **Black** code formatter. To format the code, run:
    ```bash
    make format
    ```

*   **Linting:** The project uses **Flake8** for linting. To check the code for style issues, run:
    ```bash
    make lint
    ```

*   **Project Structure:**
    *   `src/agent`: Contains the core agent functionality.
        *   `guardian_agent.py`: The main `LegendGuardianAgent` class.
        *   `clients`: Contains clients for interacting with external services like Legend Engine and SDLC.
    *   `src/api`: Contains the FastAPI web service.
        *   `main.py`: The main API application.
    *   `src/config`: Contains configuration management.
    *   `tests`: Contains all the tests for the project.
    *   `main.py`: The main entry point for running the application.
    *   `requirements.txt`: The list of Python dependencies.
    *   `Dockerfile`: The Dockerfile for building the application image.
    *   `docker-compose.yml`: The Docker Compose file for running the application and its dependencies.
    *   `Makefile`: The Makefile with common development commands.
