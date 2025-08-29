"""Health endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app
from src.settings import Settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = Settings()
    settings.api_key = "test-key"
    settings.valid_api_keys = ["test-key"]
    return settings


def test_health_endpoint_success(client):
    """Test health endpoint returns success."""
    with patch("src.api.routers.health.check_service_health") as mock_check:
        mock_check.return_value = {
            "status": "up",
            "latency_ms": 10.5,
            "status_code": 200,
        }
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "degraded", "unhealthy"]
        assert "services" in data
        assert "correlation_id" in data


def test_liveness_probe(client):
    """Test liveness probe always returns alive."""
    response = client.get("/health/live")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_readiness_probe_ready(client):
    """Test readiness probe when services are ready."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        response = client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ready", "not_ready"]


def test_health_with_service_down(client):
    """Test health endpoint when a service is down."""
    with patch("src.api.routers.health.check_service_health") as mock_check:
        # Mock different service states
        mock_check.side_effect = [
            {"status": "up", "latency_ms": 10.5, "status_code": 200},  # Engine
            {"status": "down", "error": "Connection refused"},  # SDLC
            {"status": "up", "latency_ms": 15.2, "status_code": 200},  # Depot
            {"status": "up", "latency_ms": 8.1, "status_code": 200},  # Studio
        ]
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["sdlc"]["status"] == "down"


def test_health_with_all_services_up(client):
    """Test health endpoint when all services are up."""
    with patch("src.api.routers.health.check_service_health") as mock_check:
        mock_check.return_value = {
            "status": "up",
            "latency_ms": 10.5,
            "status_code": 200,
        }
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Check all services are up
        for service in ["engine", "sdlc", "depot", "studio"]:
            assert data["services"][service]["status"] == "up"


def test_health_includes_version(client, mock_settings):
    """Test health endpoint includes version information."""
    with patch("src.api.routers.health.get_settings", return_value=mock_settings):
        with patch("src.api.routers.health.check_service_health") as mock_check:
            mock_check.return_value = {"status": "up"}
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "version" in data
            assert data["version"] == mock_settings.app_version