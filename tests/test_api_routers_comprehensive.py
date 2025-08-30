"""Comprehensive tests for API routers."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

import httpx
import pytest
import structlog
from fastapi import HTTPException
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from legend_guardian.api.main import app
from legend_guardian.config import Settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create auth headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def mock_settings():
    """Create mock settings."""
    settings = MagicMock(spec=Settings)
    settings.app_version = "1.0.0"
    settings.engine_url = "http://engine:6300"
    settings.sdlc_url = "http://sdlc:6100"
    settings.depot_url = "http://depot:6200"
    settings.studio_url = "http://studio:9000"
    settings.api_key = "test-api-key"
    return settings


class TestHealthRouter:
    """Comprehensive tests for health router."""
    
    @pytest.mark.asyncio
    async def test_check_service_health_success(self):
        """Test successful service health check."""
        from legend_guardian.api.routers.health import check_service_health
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.123
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = await check_service_health("http://test.com", "/health")
            
            assert result["status"] == "up"
            assert result["latency_ms"] == 123.0
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_check_service_health_degraded(self):
        """Test degraded service health check."""
        from legend_guardian.api.routers.health import check_service_health
        
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.elapsed.total_seconds.return_value = 0.500
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            result = await check_service_health("http://test.com", "/health")
            
            assert result["status"] == "degraded"
            assert result["latency_ms"] == 500.0
            assert result["status_code"] == 503
    
    @pytest.mark.asyncio
    async def test_check_service_health_down(self):
        """Test service down health check."""
        from legend_guardian.api.routers.health import check_service_health
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client_class.return_value = mock_client
            
            result = await check_service_health("http://test.com", "/health")
            
            assert result["status"] == "down"
            assert "error" in result
            assert "Connection refused" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_service_health_timeout(self):
        """Test service health check timeout."""
        from legend_guardian.api.routers.health import check_service_health
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.TimeoutException("Request timeout")
            mock_client_class.return_value = mock_client
            
            result = await check_service_health("http://test.com", "/health", timeout=1.0)
            
            assert result["status"] == "down"
            assert "Request timeout" in result["error"]
    
    def test_health_check_endpoint(self, client, mock_settings):
        """Test main health check endpoint."""
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('legend_guardian.api.routers.health.check_service_health') as mock_check:
            
            # Mock all services as healthy
            mock_check.return_value = {
                "status": "up",
                "latency_ms": 50.0,
                "status_code": 200
            }
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "ok"
            assert data["version"] == "1.0.0"
            assert "services" in data
            assert "correlation_id" in data
    
    def test_health_check_with_degraded_services(self, client, mock_settings):
        """Test health check with degraded services."""
        from unittest.mock import AsyncMock
        
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('legend_guardian.api.routers.health.asyncio.gather', new_callable=AsyncMock) as mock_gather:
            
            # Mix of healthy and degraded services
            mock_gather.return_value = [
                {"status": "up", "latency_ms": 50.0},
                {"status": "degraded", "latency_ms": 1000.0},
                {"status": "up", "latency_ms": 60.0},
                {"status": "up", "latency_ms": 40.0}
            ]
            
            response = client.get("/health")
            
            data = response.json()
            assert data["status"] == "degraded"
    
    def test_health_check_with_down_services(self, client, mock_settings):
        """Test health check with down services."""
        from unittest.mock import AsyncMock
        
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('legend_guardian.api.routers.health.asyncio.gather', new_callable=AsyncMock) as mock_gather:
            
            # Mix including down services
            mock_gather.return_value = [
                {"status": "up", "latency_ms": 50.0},
                {"status": "down", "error": "Connection refused"},
                {"status": "up", "latency_ms": 60.0},
                {"status": "degraded", "latency_ms": 500.0}
            ]
            
            response = client.get("/health")
            
            data = response.json()
            assert data["status"] == "unhealthy"
    
    def test_health_check_with_exceptions(self, client, mock_settings):
        """Test health check with service check exceptions."""
        from unittest.mock import AsyncMock
        
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('legend_guardian.api.routers.health.asyncio.gather', new_callable=AsyncMock) as mock_gather:
            
            # Some checks return exceptions
            mock_gather.return_value = [
                {"status": "up", "latency_ms": 50.0},
                Exception("Network error"),
                {"status": "up", "latency_ms": 60.0},
                RuntimeError("Service unavailable")
            ]
            
            response = client.get("/health")
            
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["services"]["sdlc"]["status"] == "down"
            assert "Network error" in data["services"]["sdlc"]["error"]
    
    def test_liveness_probe(self, client):
        """Test liveness probe endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_readiness_probe_ready(self, client, mock_settings):
        """Test readiness probe when services are ready."""
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('httpx.AsyncClient') as mock_client_class:
            
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            
            # Mock successful responses
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            response = client.get("/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
    
    def test_readiness_probe_not_ready(self, client, mock_settings):
        """Test readiness probe when services are not ready."""
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('httpx.AsyncClient') as mock_client_class:
            
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ConnectError("Connection refused")
            mock_client_class.return_value = mock_client
            
            response = client.get("/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"
    
    def test_readiness_probe_service_error(self, client, mock_settings):
        """Test readiness probe with service returning error."""
        with patch('legend_guardian.api.routers.health.get_settings', return_value=mock_settings), \
             patch('httpx.AsyncClient') as mock_client_class:
            
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            
            # First call returns 500, second succeeds
            mock_response1 = MagicMock()
            mock_response1.status_code = 500
            mock_response2 = MagicMock()
            mock_response2.status_code = 200
            
            mock_client.get.side_effect = [mock_response1, mock_response2]
            mock_client_class.return_value = mock_client
            
            response = client.get("/health/ready")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "not_ready"


class TestIntentRouter:
    """Comprehensive tests for intent router."""
    
    def test_process_intent_success(self, client):
        """Test successful intent processing."""
        from legend_guardian.api.routers.intent import router
        from legend_guardian.api.deps import verify_api_key
        from legend_guardian.api.main import app
        
        # Override the dependency
        app.dependency_overrides[verify_api_key] = lambda: "test-key"
        
        try:
            with patch('legend_guardian.api.routers.intent.AgentOrchestrator') as mock_orch_class:
                mock_orch = mock_orch_class.return_value
                # parse_intent returns a list of steps
                mock_result = [
                    {"action": "create_workspace", "params": {}},
                    {"action": "create_model", "params": {"name": "Person"}}
                ]
                from unittest.mock import AsyncMock
                mock_orch.parse_intent = AsyncMock(return_value=mock_result)
                mock_orch.execute_step = AsyncMock(return_value={"success": True})
                
                response = client.post(
                    "/intent/",
                    json={
                        "prompt": "Create a Person model",
                        "context": {"project": "test"},
                        "execute": False
                    },
                    headers={"X-API-Key": "test-key"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "correlation_id" in data
                assert data["prompt"] == "Create a Person model"
                assert "plan" in data
                assert "actions" in data
        finally:
            # Clean up the override
            app.dependency_overrides.clear()


class TestWebhooksRouter:
    """Comprehensive tests for webhooks router."""
    
    @pytest.mark.skip(reason="GitHub webhook endpoint not implemented")
    def test_github_webhook_pull_request(self, client):
        """Test GitHub pull request webhook - SKIPPED: Not implemented."""
        pass
    
    @pytest.mark.skip(reason="GitHub webhook endpoint not implemented")
    def test_github_webhook_push(self, client):
        """Test GitHub push webhook - SKIPPED: Not implemented."""
        pass
    
    def test_gitlab_webhook_merge_request(self, client):
        """Test GitLab merge request webhook."""
        payload = {
            "object_kind": "merge_request",
            "event_name": "merge_request",
            "user": {
                "name": "Test User",
                "username": "testuser"
            },
            "project": {
                "id": 123,
                "name": "test-project",
                "path_with_namespace": "org/test-project"
            },
            "object_attributes": {
                "id": 456,
                "iid": 78,
                "title": "Add feature",
                "state": "opened",
                "merge_status": "can_be_merged",
                "source_branch": "feature",
                "target_branch": "main"
            }
        }
        
        response = client.post(
            "/webhooks/gitlab",
            json=payload,
            headers={"X-Gitlab-Event": "Merge Request Hook"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["object_kind"] == "merge_request"
        assert data["result"]["processed"] is True
        assert data["result"]["action"] == "compile_and_comment"
    
    def test_gitlab_webhook_push(self, client):
        """Test GitLab push webhook."""
        payload = {
            "object_kind": "push",
            "event_name": "push",
            "project": {
                "id": 123,
                "name": "test-project",
                "path_with_namespace": "org/test-project"
            },
            "commits": [
                {
                    "id": "abc123",
                    "message": "Update model",
                    "author": {"name": "Test User"}
                }
            ]
        }
        
        response = client.post(
            "/webhooks/gitlab",
            json=payload,
            headers={"X-Gitlab-Event": "Push Hook"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["object_kind"] == "push"
        assert data["result"]["processed"] is True
        assert data["result"]["action"] == "validate_commits"
        assert data["result"]["commit_count"] == 1
    
    def test_sdlc_webhook_review_created(self, client):
        """Test SDLC review created webhook."""
        payload = {
            "event_type": "review.created",
            "project_id": "test-project",
            "workspace_id": "test-workspace",
            "review_id": "review-123",
            "user": "testuser",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {}
        }
        
        response = client.post("/webhooks/sdlc", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["event_type"] == "review.created"
        assert data["result"]["processed"] is True
        assert data["result"]["action"] == "compile_and_test"
        assert data["result"]["review_id"] == "review-123"
    
    def test_sdlc_webhook_review_merged(self, client):
        """Test SDLC review merged webhook."""
        payload = {
            "event_type": "review.merged",
            "project_id": "test-project",
            "workspace_id": "test-workspace", 
            "review_id": "review-456",
            "user": "testuser",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {}
        }
        
        response = client.post("/webhooks/sdlc", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["event_type"] == "review.merged"
        assert data["result"]["processed"] is True
        assert data["result"]["action"] == "deploy_service"
        assert data["result"]["review_id"] == "review-456"
    
    def test_custom_webhook_deployment(self, client):
        """Test custom deployment webhook."""
        payload = {
            "environment": "production",
            "service": "legend-engine",
            "version": "1.0.0"
        }
        
        response = client.post("/webhooks/custom/deployment", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["result"]["webhook_id"] == "deployment"
        assert data["result"]["processed"] is True
        assert data["result"]["action"] == "trigger_deployment"
    
    @pytest.mark.skip(reason="Legend webhook endpoint not implemented")
    def test_legend_webhook_model_update(self, client):
        """Test Legend model update webhook - SKIPPED: Not implemented."""
        pass


class TestFlowsRouter:
    """Comprehensive tests for flows router."""
    
    def test_execute_flow_ingest_publish(self, client):
        """Test ingest and publish flow execution."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id, get_project_id, get_workspace_id
        from legend_guardian.api.main import app
        
        request_data = {
            "csv_data": "id,name\n1,John\n2,Jane",
            "model_name": "Customer",
            "service_path": "/api/service/customer",
            "mapping_name": "CustomerMapping"
        }
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        app.dependency_overrides[get_project_id] = lambda: "test-project"
        app.dependency_overrides[get_workspace_id] = lambda: "test-workspace"
        
        try:
            with patch('legend_guardian.api.routers.flows.AgentOrchestrator') as mock_orch_class:
                mock_orch = mock_orch_class.return_value
                mock_orch.execute_step = AsyncMock(return_value={
                    "success": True,
                    "message": "Step completed"
                })
                
                response = client.post(
                    "/flows/usecase1/ingest-publish",
                    json=request_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["use_case"] == "ingest_publish"
                assert data["status"] == "completed"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
    
    def test_execute_flow_safe_rollout(self, client):
        """Test safe rollout flow execution."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id, get_project_id, get_workspace_id
        from legend_guardian.api.main import app
        
        request_data = {
            "model_path": "model::Customer",
            "changes": {
                "add_field": "email",
                "field_type": "String"
            },
            "keep_v1": True
        }
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        app.dependency_overrides[get_project_id] = lambda: "test-project"
        app.dependency_overrides[get_workspace_id] = lambda: "test-workspace"
        
        try:
            with patch('legend_guardian.api.routers.flows.AgentOrchestrator') as mock_orch_class:
                mock_orch = mock_orch_class.return_value
                mock_orch.execute_step = AsyncMock(return_value={
                    "success": True,
                    "message": "Step completed"
                })
                
                response = client.post(
                    "/flows/usecase2/safe-rollout",
                    json=request_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["use_case"] == "safe_rollout"
                assert data["status"] == "completed"
                assert data["v1_maintained"] is True
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
    
    def test_get_model_reuse_flow(self, client):
        """Test model reuse flow execution."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id
        from legend_guardian.api.main import app
        
        request_data = {
            "search_query": "Customer model",
            "target_format": "avro",
            "service_name": "customer-service"
        }
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        
        try:
            with patch('legend_guardian.api.routers.flows.AgentOrchestrator') as mock_orch_class:
                mock_orch = mock_orch_class.return_value
                mock_orch.execute_step = AsyncMock(return_value={
                    "success": True,
                    "message": "Step completed"
                })
                
                response = client.post(
                    "/flows/usecase3/model-reuse",
                    json=request_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["use_case"] == "model_reuse"
                assert data["status"] == "completed"
                assert data["schema_format"] == "avro"
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()


class TestAdapterRouters:
    """Comprehensive tests for adapter routers."""
    
    def test_engine_compile(self, client):
        """Test Engine compile endpoint."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id
        from legend_guardian.api.main import app
        
        compile_data = {
            "pure": "Class Person { firstName: String[1]; lastName: String[1]; }",
            "project_id": "test-project",
            "workspace_id": "test-workspace"
        }
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        
        try:
            with patch('legend_guardian.api.routers.adapters_engine.EngineClient') as mock_client_class:
                # Mock the client instance and its methods
                mock_client = AsyncMock()
                mock_client.compile = AsyncMock(return_value={
                    "status": "success",
                    "details": {"compiled": True},
                    "errors": []
                })
                mock_client_class.return_value = mock_client
                
                response = client.post(
                    "/adapters/engine/compile",
                    json=compile_data
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["ok"] is True
                assert "details" in data
                
                # Verify the client was instantiated and called correctly
                mock_client_class.assert_called_once()
                mock_client.compile.assert_called_once_with(
                    pure=compile_data["pure"],
                    project_id=compile_data["project_id"],
                    workspace_id=compile_data["workspace_id"]
                )
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
    
    def test_sdlc_list_projects(self, client):
        """Test SDLC list projects endpoint."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id
        from legend_guardian.api.main import app
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        
        try:
            with patch('legend_guardian.api.routers.adapters_sdlc.SDLCClient') as mock_client_class:
                # Mock the client instance and its methods
                mock_client = AsyncMock()
                mock_client.list_projects = AsyncMock(return_value=[
                    {
                        "projectId": "test-project-123",
                        "name": "Test Project",
                        "description": "A test project",
                        "groupId": "com.example",
                        "artifactId": "test-project"
                    }
                ])
                mock_client_class.return_value = mock_client
                
                response = client.get("/adapters/sdlc/projects")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["projectId"] == "test-project-123"
                assert data[0]["name"] == "Test Project"
                
                # Verify the client was instantiated and called correctly
                mock_client_class.assert_called_once()
                mock_client.list_projects.assert_called_once()
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
    
    def test_depot_search(self, client):
        """Test Depot search endpoint."""
        from legend_guardian.api.deps import verify_api_key, get_correlation_id
        from legend_guardian.api.main import app
        
        # Override dependencies
        app.dependency_overrides[verify_api_key] = lambda: "test-api-key"
        app.dependency_overrides[get_correlation_id] = lambda: "test-correlation-id"
        
        try:
            with patch('legend_guardian.api.routers.adapters_depot.DepotClient') as mock_client_class:
                # Mock the client instance and its methods
                mock_client = AsyncMock()
                mock_client.search = AsyncMock(return_value=[
                    {
                        "groupId": "com.example",
                        "artifactId": "shared-model",
                        "version": "1.0.0",
                        "entities": ["Person", "Address"]
                    }
                ])
                mock_client_class.return_value = mock_client
                
                response = client.get(
                    "/adapters/depot/search",
                    params={"q": "Person", "limit": 20}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["groupId"] == "com.example"
                assert data[0]["artifactId"] == "shared-model"
                
                # Verify the client was instantiated and called correctly
                mock_client_class.assert_called_once()
                mock_client.search.assert_called_once_with(
                    query="Person",
                    limit=20
                )
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()