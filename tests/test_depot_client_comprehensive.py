"""Comprehensive tests for Legend Depot client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
import httpx
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients.depot import DepotClient
from legend_guardian.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        depot_url="http://test-depot:6200",
        depot_token="test-token",
        request_timeout=30.0,
    )


@pytest.fixture
def depot_client(settings):
    """Create depot client instance."""
    return DepotClient(settings)


@pytest.mark.asyncio
async def test_depot_client_initialization(settings):
    """Test depot client initialization."""
    client = DepotClient(settings)
    assert client.base_url == "http://test-depot:6200"
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Accept"] == "application/json"
    assert client.headers["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_depot_client_initialization_without_token():
    """Test depot client initialization without token."""
    settings = Settings(depot_url="http://test-depot:6200")
    client = DepotClient(settings)
    assert "Authorization" not in client.headers


@pytest.mark.asyncio
async def test_get_info(depot_client):
    """Test get_info method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"version": "1.0.0", "status": "healthy"}
        
        result = await depot_client.get_info()
        
        mock_request.assert_called_once_with("GET", "/api/info")
        assert result["version"] == "1.0.0"
        assert result["status"] == "healthy"


@pytest.mark.asyncio
async def test_search(depot_client):
    """Test search method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = [
            {"id": "model1", "name": "Test Model 1"},
            {"id": "model2", "name": "Test Model 2"}
        ]
        
        result = await depot_client.search("test", limit=10, project_filter="my-project")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/search",
            params={"q": "test", "limit": 10, "project": "my-project"}
        )
        assert len(result) == 2
        assert result[0]["id"] == "model1"


@pytest.mark.asyncio
async def test_search_without_filter(depot_client):
    """Test search without project filter."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = []
        
        await depot_client.search("test")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/search",
            params={"q": "test", "limit": 20}
        )


@pytest.mark.asyncio
async def test_list_projects(depot_client):
    """Test list_projects method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = [
            {"id": "proj1", "name": "Project 1"},
            {"id": "proj2", "name": "Project 2"}
        ]
        
        result = await depot_client.list_projects()
        
        mock_request.assert_called_once_with("GET", "/api/projects")
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_project(depot_client):
    """Test get_project method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"id": "proj1", "name": "Project 1"}
        
        result = await depot_client.get_project("proj1")
        
        mock_request.assert_called_once_with("GET", "/api/projects/proj1")
        assert result["id"] == "proj1"


@pytest.mark.asyncio
async def test_list_versions(depot_client):
    """Test list_versions method."""
    with patch.object(depot_client, '_request') as mock_request:
        # Test with list response
        mock_request.return_value = [
            {"version": "1.0.0"},
            {"version": "1.1.0"}
        ]
        
        result = await depot_client.list_versions("proj1", limit=10)
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions",
            params={"limit": 10}
        )
        assert result == ["1.0.0", "1.1.0"]


@pytest.mark.asyncio
async def test_list_versions_dict_response(depot_client):
    """Test list_versions with dict response."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"versions": ["2.0.0", "2.1.0"]}
        
        result = await depot_client.list_versions("proj1")
        
        assert result == ["2.0.0", "2.1.0"]


@pytest.mark.asyncio
async def test_get_latest_version(depot_client):
    """Test get_latest_version method."""
    with patch.object(depot_client, '_request') as mock_request:
        # Test dict response with version key
        mock_request.return_value = {"version": "3.0.0"}
        
        result = await depot_client.get_latest_version("proj1")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/latest"
        )
        assert result == "3.0.0"


@pytest.mark.asyncio
async def test_get_latest_version_version_id(depot_client):
    """Test get_latest_version with versionId key."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"versionId": "3.1.0"}
        
        result = await depot_client.get_latest_version("proj1")
        assert result == "3.1.0"


@pytest.mark.asyncio
async def test_get_latest_version_string(depot_client):
    """Test get_latest_version with string response."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = "3.2.0"
        
        result = await depot_client.get_latest_version("proj1")
        assert result == "3.2.0"


@pytest.mark.asyncio
async def test_get_entities(depot_client):
    """Test get_entities method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = [
            {"type": "Class", "path": "com.example.Model"}
        ]
        
        result = await depot_client.get_entities("proj1", "1.0.0", entity_filter="Class")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/1.0.0/entities",
            params={"type": "Class"}
        )
        assert len(result) == 1


@pytest.mark.asyncio
async def test_get_entity(depot_client):
    """Test get_entity method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"path": "com.example.Model", "content": "..."}
        
        result = await depot_client.get_entity("proj1", "1.0.0", "com.example.Model")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/1.0.0/entities/com.example.Model"
        )
        assert result["path"] == "com.example.Model"


@pytest.mark.asyncio
async def test_get_dependencies(depot_client):
    """Test get_dependencies method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = [
            {"project": "dep1", "version": "1.0.0"}
        ]
        
        result = await depot_client.get_dependencies("proj1", "1.0.0", transitive=True)
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/1.0.0/dependencies",
            params={"transitive": True}
        )
        assert len(result) == 1


@pytest.mark.asyncio
async def test_get_dependents(depot_client):
    """Test get_dependents method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = [
            {"project": "dependent1", "version": "2.0.0"}
        ]
        
        result = await depot_client.get_dependents("proj1", "1.0.0")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/1.0.0/dependents"
        )
        assert len(result) == 1


@pytest.mark.asyncio
async def test_publish(depot_client):
    """Test publish method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"status": "success", "version": "1.0.0"}
        
        entities = [{"type": "Class", "path": "com.example.Model"}]
        dependencies = [{"project": "dep1", "version": "1.0.0"}]
        
        result = await depot_client.publish(
            "proj1", "1.0.0", entities=entities, dependencies=dependencies
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/publish",
            json_data={
                "projectId": "proj1",
                "version": "1.0.0",
                "entities": entities,
                "dependencies": dependencies
            }
        )
        assert result["status"] == "success"


@pytest.mark.asyncio
async def test_publish_minimal(depot_client):
    """Test publish with minimal parameters."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        await depot_client.publish("proj1", "1.0.0")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/publish",
            json_data={
                "projectId": "proj1",
                "version": "1.0.0"
            }
        )


@pytest.mark.asyncio
async def test_get_metadata(depot_client):
    """Test get_metadata method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"created": "2023-01-01", "author": "test"}
        
        result = await depot_client.get_metadata("proj1", "1.0.0")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/versions/1.0.0/metadata"
        )
        assert result["author"] == "test"


@pytest.mark.asyncio
async def test_resolve_coordinates(depot_client):
    """Test resolve_coordinates method."""
    with patch.object(depot_client, '_request') as mock_request:
        mock_request.return_value = {"project": "resolved-proj", "version": "1.0.0"}
        
        result = await depot_client.resolve_coordinates(
            "com.example", "my-artifact", "1.0.0"
        )
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/coordinates/com.example/my-artifact/1.0.0"
        )
        assert result["project"] == "resolved-proj"


@pytest.mark.asyncio
async def test_request_with_error(depot_client):
    """Test _request with error response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_client.request.return_value = mock_response
        
        # The depot client retries on errors, so we expect a RetryError
        from tenacity import RetryError
        with pytest.raises(RetryError):
            await depot_client._request("GET", "/api/test")


@pytest.mark.asyncio
async def test_request_with_json_response(depot_client):
    """Test _request with JSON response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}
        mock_client.request.return_value = mock_response
        
        result = await depot_client._request("GET", "/api/test")
        
        assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_request_with_text_response(depot_client):
    """Test _request with text response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_client.request.return_value = mock_response
        
        result = await depot_client._request("GET", "/api/test")
        
        assert result == "Plain text response"


@pytest.mark.asyncio
async def test_request_retry_on_failure(depot_client):
    """Test that _request retries on failure."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # First two calls fail, third succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server error"
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.headers = {"content-type": "application/json"}
        mock_response_success.json.return_value = {"status": "success"}
        
        mock_client.request.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]
        
        result = await depot_client._request("GET", "/api/test")
        
        assert result == {"status": "success"}
        assert mock_client.request.call_count == 3