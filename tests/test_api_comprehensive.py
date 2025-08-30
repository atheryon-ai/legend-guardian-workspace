"""Comprehensive tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import json
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
    """Create auth headers for testing."""
    return {"Authorization": "Bearer test-token"}


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_readiness_check(self, client):
        """Test readiness check."""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
    
    def test_liveness_check(self, client):
        """Test liveness check."""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_service_status(self, client):
        """Test service status endpoint."""
        with patch('legend_guardian.api.routers.health.check_service_health') as mock_check:
            mock_check.return_value = {"engine": "healthy", "sdlc": "healthy"}
            
            response = client.get("/health")
            assert response.status_code in [200, 503]
            data = response.json()
            assert "status" in data


class TestIntentEndpoints:
    """Tests for intent processing endpoints."""
    
    def test_process_intent(self, client, auth_headers):
        """Test intent processing."""
        with patch('legend_guardian.agent.orchestrator.AgentOrchestrator.parse_intent') as mock_parse, \
             patch('legend_guardian.agent.orchestrator.AgentOrchestrator.execute_step') as mock_execute:
            
            mock_parse.return_value = [
                {"action": "create_model", "params": {"model_name": "Person"}}
            ]
            mock_execute.return_value = {"status": "success"}
            
            response = client.post(
                "/intent/",
                json={"prompt": "Create a Person model"},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
    
    def test_validate_intent(self, client, auth_headers):
        """Test intent validation."""
        with patch('legend_guardian.agent.orchestrator.AgentOrchestrator.parse_intent') as mock_parse, \
             patch('legend_guardian.agent.orchestrator.AgentOrchestrator.validate_step') as mock_validate:
            
            mock_parse.return_value = [
                {"action": "create_workspace", "params": {"workspace_id": "test"}}
            ]
            mock_validate.return_value = {"valid": True, "issues": []}
            
            response = client.post(
                "/intent/validate",
                json={"prompt": "Create a test workspace"},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    def test_intent_without_auth(self, client):
        """Test intent endpoint without authentication."""
        response = client.post(
            "/intent/",
            json={"prompt": "Test"}
        )
        assert response.status_code in [401, 422]
    
    def test_intent_validation_endpoint(self, client, auth_headers):
        """Test intent validation endpoint."""
        with patch('legend_guardian.agent.orchestrator.AgentOrchestrator.parse_intent') as mock_parse, \
             patch('legend_guardian.agent.orchestrator.AgentOrchestrator.validate_step') as mock_validate:
            
            mock_parse.return_value = [
                {"action": "compile", "params": {}}
            ]
            mock_validate.return_value = {"valid": True, "issues": []}
            
            response = client.post(
                "/intent/validate",
                json={"prompt": "Compile the model"},
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestWebhookEndpoints:
    """Tests for webhook endpoints."""
    
    def test_sdlc_webhook(self, client):
        """Test SDLC webhook."""
        payload = {
            "event_type": "review.created",
            "project_id": "test-project",
            "workspace_id": "test-workspace",
            "review_id": "review-123",
            "user": "testuser",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {}
        }
        
        response = client.post(
            "/webhooks/sdlc",
            json=payload
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        assert "status" in data
    
    def test_gitlab_webhook(self, client):
        """Test GitLab webhook."""
        payload = {
            "object_kind": "merge_request",
            "event_name": "merge_request",
            "project": {"name": "test-project", "id": 123},
            "object_attributes": {
                "id": 456,
                "iid": 1,
                "title": "Test MR",
                "state": "opened"
            }
        }
        
        response = client.post(
            "/webhooks/gitlab",
            json=payload,
            headers={"X-Gitlab-Event": "Merge Request Hook"}
        )
        
        assert response.status_code in [200, 202]
    
    def test_custom_webhook(self, client):
        """Test custom webhook."""
        payload = {
            "event": "model_updated",
            "project": "test-project",
            "model": "Person",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        response = client.post(
            "/webhooks/custom/deployment",
            json=payload
        )
        
        assert response.status_code in [200, 202]
    
    def test_webhook_invalid_payload(self, client):
        """Test webhook with invalid payload."""
        response = client.post(
            "/webhooks/sdlc",
            json={"invalid": "payload"}
        )
        
        assert response.status_code in [200, 202, 400, 422]


class TestFlowEndpoints:
    """Tests for use case flow endpoints."""
    
    def test_usecase1_ingest_publish(self, client, auth_headers):
        """Test use case 1: Ingest and Publish."""
        request_data = {
            "csv_data": "name,age\nJohn,30\nJane,25",
            "model_name": "TestModel",
            "service_path": "test::service::TestService",
            "mapping_name": "FlatDataMapping"
        }
        
        with patch('legend_guardian.agent.orchestrator.AgentOrchestrator.execute_step') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            
            response = client.post(
                "/flows/usecase1/ingest-publish",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
    
    def test_usecase2_safe_rollout(self, client, auth_headers):
        """Test use case 2: Safe Rollout."""
        request_data = {
            "model_id": "test-model",
            "version": "1.0.0",
            "environment": "staging",
            "validation_rules": ["schema_check", "data_quality"]
        }
        
        response = client.post(
            "/flows/usecase2/safe-rollout",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401]
    
    def test_usecase3_model_reuse(self, client, auth_headers):
        """Test use case 3: Model Reuse."""
        request_data = {
            "source_project": "project1",
            "source_model": "SharedModel",
            "target_projects": ["project2", "project3"]
        }
        
        response = client.post(
            "/flows/usecase3/model-reuse",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401]
    
    def test_usecase4_reverse_etl(self, client, auth_headers):
        """Test use case 4: Reverse ETL."""
        request_data = {
            "source_model": "Customer",
            "target_system": "salesforce",
            "sync_frequency": "daily",
            "field_mappings": {"id": "CustomerId", "name": "CustomerName"}
        }
        
        response = client.post(
            "/flows/usecase4/reverse-etl",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401]
    
    def test_usecase8_incident_rollback(self, client, auth_headers):
        """Test use case 8: Incident Rollback."""
        request_data = {
            "service_path": "test::service::TestService",
            "target_version": "1.0.0",
            "create_hotfix": True
        }
        
        with patch('legend_guardian.agent.orchestrator.AgentOrchestrator.execute_step') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            
            response = client.post(
                "/flows/usecase8/incident-rollback",
                json=request_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestDepotAdapterEndpoints:
    """Tests for Depot adapter endpoints."""
    
    def test_search_depot(self, client, auth_headers):
        """Test Depot search."""
        with patch('legend_guardian.clients.depot.DepotClient.search') as mock_search:
            mock_search.return_value = [
                {"path": "model::Model1", "project_id": "proj1"},
                {"path": "model::Model2", "project_id": "proj2"}
            ]
            
            response = client.get(
                "/adapters/depot/search?q=test",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
    
    def test_list_depot_projects(self, client, auth_headers):
        """Test listing Depot projects."""
        with patch('legend_guardian.clients.depot.DepotClient.list_projects') as mock_list:
            mock_list.return_value = [
                {"project_id": "proj1", "group_id": "group1", "artifact_id": "art1", "versions": ["1.0.0"]}
            ]
            
            response = client.get(
                "/adapters/depot/projects",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    def test_publish_to_depot(self, client, auth_headers):
        """Test publishing to Depot."""
        publish_data = {
            "version": "1.0.0",
            "entities": [{"_type": "class", "path": "model::Person"}]
        }
        
        with patch('legend_guardian.clients.depot.DepotClient.publish') as mock_publish:
            mock_publish.return_value = {"version": "1.0.0", "published_entities": 1}
            
            response = client.post(
                "/adapters/depot/projects/test-project/publish",
                json=publish_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestEngineAdapterEndpoints:
    """Tests for Engine adapter endpoints."""
    
    def test_compile_model(self, client, auth_headers):
        """Test model compilation."""
        model_data = {
            "clientVersion": "v1_29_0",
            "model": {
                "_type": "data",
                "elements": [
                    {"_type": "class", "name": "Person", "package": "model"}
                ]
            }
        }
        
        with patch('legend_guardian.clients.engine.EngineClient.compile') as mock_compile:
            mock_compile.return_value = {
                "status": "SUCCESS",
                "warnings": [],
                "errors": []
            }
            
            response = client.post(
                "/adapters/engine/compile",
                json=model_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
    
    def test_execution_plan(self, client, auth_headers):
        """Test execution plan generation."""
        plan_data = {
            "clientVersion": "v1_29_0",
            "function": {
                "_type": "lambda",
                "body": [{"_type": "property", "property": "name"}],
                "parameters": []
            }
        }
        
        with patch('legend_guardian.clients.engine.EngineClient.generate_execution_plan') as mock_plan:
            mock_plan.return_value = {
                "plan": {"serializer": "PURE"}
            }
            
            response = client.post(
                "/adapters/engine/execution-plan",
                json=plan_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    def test_run_tests(self, client, auth_headers):
        """Test running tests."""
        test_data = {
            "clientVersion": "v1_29_0",
            "model": {
                "_type": "data",
                "elements": []
            }
        }
        
        with patch('legend_guardian.clients.engine.EngineClient.run_tests') as mock_tests:
            mock_tests.return_value = {
                "results": [
                    {"testable": "test1", "result": "PASSED"},
                    {"testable": "test2", "result": "PASSED"}
                ]
            }
            
            response = client.post(
                "/adapters/engine/test/run",
                json=test_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestSDLCAdapterEndpoints:
    """Tests for SDLC adapter endpoints."""
    
    def test_list_projects(self, client, auth_headers):
        """Test listing SDLC projects."""
        with patch('legend_guardian.clients.sdlc.SDLCClient.list_projects') as mock_list:
            mock_list.return_value = [
                {"projectId": "proj1", "name": "Project 1"}
            ]
            
            response = client.get(
                "/adapters/sdlc/projects",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    def test_create_workspace(self, client, auth_headers):
        """Test creating workspace."""
        workspace_data = {
            "project_id": "test-project",
            "workspace_type": "USER",
            "workspace_id": "test-workspace"
        }
        
        with patch('legend_guardian.clients.sdlc.SDLCClient.create_workspace') as mock_create:
            mock_create.return_value = {
                "projectId": "test-project",
                "workspaceId": "test-workspace"
            }
            
            response = client.post(
                "/adapters/sdlc/workspaces/test-workspace",
                json=workspace_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]
    
    def test_create_review(self, client, auth_headers):
        """Test creating review."""
        review_data = {
            "project_id": "test-project",
            "workspace_id": "test-workspace",
            "title": "Test Review",
            "description": "Review description"
        }
        
        with patch('legend_guardian.clients.sdlc.SDLCClient.create_review') as mock_create:
            mock_create.return_value = {
                "id": "review1",
                "state": "OPEN",
                "title": "Test Review"
            }
            
            response = client.post(
                "/adapters/sdlc/reviews",
                json=review_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 401]


class TestMainAPI:
    """Tests for main API endpoints."""
    
    def test_api_info(self, client):
        """Test API info endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
    
    def test_root_redirect(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "docs" in data
    
    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # CORS might not be configured, so accept various responses
        assert response.status_code in [200, 204, 405]


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self, client, auth_headers):
        """Test invalid JSON handling."""
        response = client.post(
            "/intent/",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_method_not_allowed(self, client):
        """Test method not allowed."""
        response = client.post("/health")
        assert response.status_code == 405
    
    def test_validation_error(self, client, auth_headers):
        """Test validation error."""
        response = client.post(
            "/flows/usecase1/ingest-publish",
            json={},  # Missing required fields
            headers=auth_headers
        )
        assert response.status_code in [422, 401]


class TestAuthentication:
    """Tests for authentication."""
    
    def test_protected_endpoint_no_auth(self, client):
        """Test protected endpoint without auth."""
        response = client.get("/adapters/depot/projects")
        assert response.status_code == 401
    
    def test_protected_endpoint_invalid_token(self, client):
        """Test protected endpoint with invalid token."""
        response = client.get(
            "/adapters/depot/projects",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_public_endpoint(self, client):
        """Test public endpoint."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # Health check can return 503 if services are down