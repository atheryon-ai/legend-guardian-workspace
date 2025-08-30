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
        
        pure_code = "Class model::Person { name: String[1]; }"
        result = await engine_client.compile(pure_code)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/compilation/compile",
            json_data={
                "code": pure_code,
                "isolatedLambdas": {}
            }
        )
        assert result["status"] == "success"


@pytest.mark.asyncio
async def test_transform_to_schema(engine_client):
    """Test transform_to_schema method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "schema": {
                "tables": [{"name": "person", "columns": []}]
            }
        }
        
        schema_type = "jsonSchema"
        class_path = "model::Person"
        result = await engine_client.transform_to_schema(schema_type, class_path, include_dependencies=False)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/schemaGeneration/jsonSchema",
            json_data={
                "classPath": class_path,
                "includeDependencies": False
            }
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
        mapping = "mapping::test"
        runtime = "runtime::test"
        
        result = await engine_client.execute_query(query, mapping, runtime, context={})
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/execute",
            json_data={
                "query": query,
                "mapping": mapping,
                "runtime": runtime,
                "context": {}
            }
        )
        assert result["result"]["values"][0][0] == "John"


@pytest.mark.asyncio
async def test_execute_query_minimal(engine_client):
    """Test execute_query with minimal parameters."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {"result": {"values": []}}
        
        await engine_client.execute_query("query", "mapping::test", "runtime::test")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/execute",
            json_data={
                "query": "query",
                "mapping": "mapping::test",
                "runtime": "runtime::test",
                "context": {}
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
        
        mapping = "mapping::test"
        runtime = "runtime::test"
        query = "model::Person.all()"
        
        result = await engine_client.generate_execution_plan(
            mapping, runtime, query
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/generatePlan",
            json_data={
                "mapping": mapping,
                "runtime": runtime,
                "query": query,
                "context": {}
            }
        )
        assert result["plan"]["_type"] == "simple"


@pytest.mark.asyncio
async def test_generate_execution_plan_minimal(engine_client):
    """Test generate_execution_plan with minimal parameters."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {"plan": {}}
        
        await engine_client.generate_execution_plan("mapping::test", "runtime::test", "query")
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/execution/generatePlan",
            json_data={
                "mapping": "mapping::test",
                "runtime": "runtime::test",
                "query": "query",
                "context": {}
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
        params = {"elements": []}
        
        result = await engine_client.run_service(service_path, params)
        
        mock_request.assert_called_once_with(
            "GET",
            "/api/service/model::MyService",
            params=params
        )
        assert result["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_generate_service_code(engine_client):
    """Test generate_service_code method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "code": "public class PersonService {}"
        }
        
        service_path = "model::PersonService"
        target = "java"
        
        result = await engine_client.generate_service_code(
            service_path, target
        )
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/codeGeneration/generate",
            json_data={
                "servicePath": service_path,
                "target": target
            }
        )
        assert "PersonService" in result


@pytest.mark.asyncio
async def test_run_tests(engine_client):
    """Test run_tests method."""
    with patch.object(engine_client, '_request') as mock_request:
        mock_request.return_value = {
            "tests": [
                {"name": "test1", "status": "PASS", "message": "Success"},
                {"name": "test2", "status": "PASS", "message": "Success"}
            ]
        }
        
        test_path = "model::TestSuite"
        
        result = await engine_client.run_tests(test_path)
        
        mock_request.assert_called_once_with(
            "POST",
            "/api/pure/v1/test/run",
            json_data={"testPath": test_path}
        )
        assert len(result) == 2
        assert result[0]["test"] == "test1"
        assert result[0]["passed"] == True


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
        
        # The method has retry decorator, so it will raise RetryError after 3 attempts
        from tenacity import RetryError
        with pytest.raises(RetryError):
            await engine_client._request("GET", "/api/test")


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
        
        assert result == {"text": "Plain text response"}


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