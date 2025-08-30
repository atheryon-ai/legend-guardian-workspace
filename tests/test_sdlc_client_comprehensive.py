"""Comprehensive tests for Legend SDLC client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients.sdlc import SDLCClient
from legend_guardian.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        sdlc_url="http://test-sdlc:6100",
        sdlc_token="test-token",
        request_timeout=30.0,
    )


@pytest.fixture
def sdlc_client(settings):
    """Create SDLC client instance."""
    return SDLCClient(settings)


@pytest.mark.asyncio
async def test_sdlc_client_initialization(settings):
    """Test SDLC client initialization."""
    client = SDLCClient(settings)
    assert client.base_url == "http://test-sdlc:6100"
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_sdlc_client_initialization_without_token():
    """Test SDLC client initialization without token."""
    settings = Settings(sdlc_url="http://test-sdlc:6100")
    client = SDLCClient(settings)
    assert "Authorization" not in client.headers


@pytest.mark.asyncio
async def test_get_info(sdlc_client):
    """Test get_info method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"version": "1.0.0", "status": "healthy"}
        
        result = await sdlc_client.get_info()
        
        mock_request.assert_called_once_with("GET", "/api/info")
        assert result["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_list_projects(sdlc_client):
    """Test list_projects method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = [
            {"projectId": "proj1", "name": "Project 1"},
            {"projectId": "proj2", "name": "Project 2"}
        ]
        
        result = await sdlc_client.list_projects()
        
        mock_request.assert_called_once_with("GET", "/api/projects")
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_project(sdlc_client):
    """Test get_project method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"projectId": "proj1", "name": "Project 1"}
        
        result = await sdlc_client.get_project("proj1")
        
        mock_request.assert_called_once_with("GET", "/api/projects/proj1")
        assert result["projectId"] == "proj1"


@pytest.mark.asyncio
async def test_create_project(sdlc_client):
    """Test create_project method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"projectId": "new-proj", "name": "New Project"}
        
        result = await sdlc_client.create_project(
            "new-proj",
            "New Project",
            description="Test project",
            tags=["test", "demo"]
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects",
            json_data={
                "projectId": "new-proj",
                "name": "New Project",
                "description": "Test project",
                "tags": ["test", "demo"]
            }
        )
        assert result["projectId"] == "new-proj"


@pytest.mark.asyncio
async def test_create_project_minimal(sdlc_client):
    """Test create_project with minimal parameters."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"projectId": "new-proj"}
        
        result = await sdlc_client.create_project("new-proj", "New Project")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects",
            json_data={
                "projectId": "new-proj",
                "name": "New Project"
            }
        )
        assert result["projectId"] == "new-proj"


@pytest.mark.asyncio
async def test_list_workspaces(sdlc_client):
    """Test list_workspaces method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = [
            {"workspaceId": "ws1", "userId": "user1"},
            {"workspaceId": "ws2", "userId": "user2"}
        ]
        
        result = await sdlc_client.list_workspaces("proj1")
        
        mock_request.assert_called_once_with("GET", "/api/projects/proj1/workspaces")
        assert len(result) == 2


@pytest.mark.asyncio
async def test_create_workspace(sdlc_client):
    """Test create_workspace method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"workspaceId": "new-ws", "userId": "user1"}
        
        result = await sdlc_client.create_workspace(
            "proj1",
            "new-ws",
            workspace_type="USER"
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/proj1/workspaces",
            json_data={
                "workspaceId": "new-ws",
                "workspaceType": "USER"
            }
        )
        assert result["workspaceId"] == "new-ws"


@pytest.mark.asyncio
async def test_create_workspace_minimal(sdlc_client):
    """Test create_workspace with minimal parameters."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"workspaceId": "new-ws"}
        
        result = await sdlc_client.create_workspace("proj1", "new-ws")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/proj1/workspaces",
            json_data={"workspaceId": "new-ws"}
        )
        assert result["workspaceId"] == "new-ws"


# get_workspace doesn't exist - removed test


@pytest.mark.asyncio
async def test_delete_workspace(sdlc_client):
    """Test delete_workspace method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"status": "deleted"}
        
        result = await sdlc_client.delete_workspace("proj1", "ws1")
        
        mock_request.assert_called_once_with(
            "DELETE",
            "/api/projects/proj1/workspaces/ws1"
        )
        assert result["status"] == "deleted"


@pytest.mark.asyncio
async def test_get_entities(sdlc_client):
    """Test get_entities method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = [
            {"path": "model::Entity1", "content": "..."},
            {"path": "model::Entity2", "content": "..."}
        ]
        
        result = await sdlc_client.get_entities("proj1", workspace_id="ws1")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/workspaces/ws1/entities"
        )
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_entities_main(sdlc_client):
    """Test get_entities for main branch."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = []
        
        result = await sdlc_client.get_entities("proj1")
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/projects/proj1/entities"
        )
        assert result == []


# get_entity doesn't exist - use upsert_entities instead


@pytest.mark.asyncio
async def test_upsert_entities(sdlc_client):
    """Test upsert_entities method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"status": "success"}
        
        entities = [{"path": "model::NewEntity", "content": {"_type": "class"}}]
        result = await sdlc_client.upsert_entities(
            "proj1",
            entities,
            workspace_id="ws1"
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/proj1/workspaces/ws1/entities",
            json_data={"entities": entities}
        )
        assert result["status"] == "success"


# update_entity doesn't exist - use upsert_entities


@pytest.mark.asyncio
async def test_delete_entity(sdlc_client):
    """Test delete_entity method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"status": "deleted"}
        
        result = await sdlc_client.delete_entity(
            "proj1",
            "model::Entity1",
            workspace_id="ws1"
        )
        
        mock_request.assert_called_once_with(
            "DELETE",
            "/api/projects/proj1/workspaces/ws1/entities/model::Entity1"
        )
        assert result["status"] == "deleted"


# get_revisions and get_revision don't exist


@pytest.mark.asyncio
async def test_create_review(sdlc_client):
    """Test create_review method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"reviewId": "review1", "status": "OPEN"}
        
        result = await sdlc_client.create_review(
            "proj1",
            "ws1",
            title="Review Title",
            description="Review Description"
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/proj1/workspaces/ws1/reviews",
            json_data={
                "title": "Review Title",
                "description": "Review Description"
            }
        )
        assert result["reviewId"] == "review1"


@pytest.mark.asyncio
async def test_merge_review(sdlc_client):
    """Test merge_review method."""
    with patch.object(sdlc_client, '_request') as mock_request:
        mock_request.return_value = {"status": "merged", "revision": "rev123"}
        
        result = await sdlc_client.merge_review("proj1", "review1")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/projects/proj1/reviews/review1/merge"
        )
        assert result["status"] == "merged"


@pytest.mark.asyncio
async def test_request_with_error(sdlc_client):
    """Test _request with error response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_client.request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            await sdlc_client._request("GET", "/api/test")
        
        assert "404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_with_json_response(sdlc_client):
    """Test _request with JSON response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"key": "value"}
        mock_client.request.return_value = mock_response
        
        result = await sdlc_client._request("GET", "/api/test")
        
        assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_request_retry(sdlc_client):
    """Test _request retry logic."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # First call fails, second succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server error"
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.headers = {"content-type": "application/json"}
        mock_response_success.json.return_value = {"status": "success"}
        
        mock_client.request.side_effect = [
            mock_response_fail,
            mock_response_success
        ]
        
        result = await sdlc_client._request("GET", "/api/test")
        
        assert result == {"status": "success"}
        assert mock_client.request.call_count == 2