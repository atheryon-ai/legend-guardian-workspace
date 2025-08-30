"""Comprehensive tests for Legend Engine client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients.engine import EngineClient
from legend_guardian.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        engine_url="http://test-engine:6300",
        engine_token="test-token",
        request_timeout=30.0,
    )


@pytest.fixture
def engine_client(settings):
    """Create engine client instance."""
    return EngineClient(settings)


@pytest.mark.asyncio
async def test_engine_client_initialization(settings):
    """Test engine client initialization."""
    client = EngineClient(settings)
    assert client.base_url == "http://test-engine:6300"
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_engine_client_initialization_without_token():
    """Test engine client initialization without token."""
    settings = Settings(engine_url="http://test-engine:6300")
    client = EngineClient(settings)
    assert "Authorization" not in client.headers


@pytest.mark.asyncio
async def test_get_info(engine_client):
    """Test get_info method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {"version": "1.0.0", "status": "healthy"}
        
        result = await engine_client.get_info()
        
        mock_request.assert_called_once_with("GET", "/api/server/v1/info")
        assert result["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_compile(engine_client):
    """Test compile method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "status": "SUCCESS",
            "warnings": [],
            "errors": []
        }
        
        model_data = {
            "_type": "data",
            "elements": [{"_type": "class", "name": "Person"}]
        }
        result = await engine_client.compile(model_data)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/compilation/compile",
            json_data=model_data
        )
        assert result["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_transform_to_schema(engine_client):
    """Test transform_to_schema method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "schema": {
                "tables": [{"name": "person", "columns": []}]
            }
        }
        
        model_data = {
            "_type": "data",
            "elements": [{"_type": "class", "name": "Person"}]
        }
        target_type = "relational"
        result = await engine_client.transform_to_schema(model_data, target_type)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/schemaGeneration/transform",
            json_data={"model": model_data, "targetType": target_type}
        )
        assert "schema" in result


@pytest.mark.asyncio
async def test_execute_query(engine_client):
    """Test execute_query method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "result": {
                "builder": {"_type": "tdsBuilder"},
                "values": [
                    ["John", 30],
                    ["Jane", 25]
                ]
            }
        }
        
        query = "model::Person.all()->project([x|$x.name, x|$x.age], ['Name', 'Age'])"
        model = {"elements": []}
        
        result = await engine_client.execute_query(query, model, mapping="mapping::test")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/execute",
            json_data={
                "func": query,
                "model": model,
                "mapping": "mapping::test"
            }
        )
        assert result["result"]["values"][0][0] == "John"


@pytest.mark.asyncio
async def test_execute_query_minimal(engine_client):
    """Test execute_query with minimal parameters."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {"result": {"values": []}}
        
        await engine_client.execute_query("query", {"elements": []})
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/execute",
            json_data={
                "func": "query",
                "model": {"elements": []}
            }
        )


@pytest.mark.asyncio
async def test_generate_execution_plan(engine_client):
    """Test generate_execution_plan method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "plan": {
                "_type": "simple",
                "authDependent": False,
                "serializer": {"name": "pure"}
            }
        }
        
        query = "model::Person.all()"
        model = {"elements": []}
        mapping = "mapping::test"
        runtime = {"_type": "runtime"}
        
        result = await engine_client.generate_execution_plan(
            query, model, mapping, runtime
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/generatePlan",
            json_data={
                "func": query,
                "model": model,
                "mapping": mapping,
                "runtime": runtime
            }
        )
        assert result["plan"]["_type"] == "simple"


@pytest.mark.asyncio
async def test_generate_execution_plan_minimal(engine_client):
    """Test generate_execution_plan with minimal parameters."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {"plan": {}}
        
        await engine_client.generate_execution_plan("query", {"elements": []})
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/generatePlan",
            json_data={
                "func": "query",
                "model": {"elements": []}
            }
        )


@pytest.mark.asyncio
async def test_run_service(engine_client):
    """Test run_service method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "status": "SUCCESS",
            "result": {"values": [["value1"], ["value2"]]}
        }
        
        service_path = "model::MyService"
        model_data = {"elements": []}
        
        result = await engine_client.run_service(service_path, model_data)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/service/runService",
            json_data={"service": service_path, "model": model_data}
        )
        assert result["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_generate_service_code(engine_client):
    """Test generate_service_code method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "code": "public class PersonService {}",
            "language": "java"
        }
        
        service_path = "model::PersonService"
        model_data = {"elements": []}
        target_language = "java"
        
        result = await engine_client.generate_service_code(
            service_path, model_data, target_language
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/generation/generateServiceCode",
            json_data={
                "service": service_path,
                "model": model_data,
                "language": target_language
            }
        )
        assert "PersonService" in result["code"]


@pytest.mark.asyncio
async def test_run_tests(engine_client):
    """Test run_tests method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "status": "SUCCESS",
            "results": [
                {"test": "test1", "status": "PASS"},
                {"test": "test2", "status": "PASS"}
            ]
        }
        
        test_data = {
            "tests": ["test1", "test2"],
            "model": {"elements": []},
            "testData": {}
        }
        
        result = await engine_client.run_tests(test_data)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/test/runTests",
            json_data=test_data
        )
        assert result["status"] == "SUCCESS"
        assert len(result["results"]) == 2


# Note: These methods don't exist in the actual EngineClient implementation


@pytest.mark.asyncio
async def test_request_with_error(engine_client):
    """Test _request with error response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_client.request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            await engine_client._request("GET", "/api/test")
        
        assert "400" in str(exc_info.value)
        assert "Bad request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_request_with_json_response(engine_client):
    """Test _request with JSON response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json; charset=utf-8"}
        mock_response.json.return_value = {"result": "success"}
        mock_client.request.return_value = mock_response
        
        result = await engine_client._request("GET", "/api/test")
        
        assert result == {"result": "success"}


@pytest.mark.asyncio
async def test_request_with_text_response(engine_client):
    """Test _request with text response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Plain text response"
        mock_client.request.return_value = mock_response
        
        result = await engine_client._request("GET", "/api/test")
        
        assert result == "Plain text response"


@pytest.mark.asyncio
async def test_request_retry_logic(engine_client):
    """Test request retry logic on failure."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # First call times out, second succeeds
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        
        mock_client.request.side_effect = [
            Exception("Connection timeout"),
            mock_response
        ]
        
        result = await engine_client._request("GET", "/api/test")
        
        assert result == {"status": "success"}
        assert mock_client.request.call_count == 2