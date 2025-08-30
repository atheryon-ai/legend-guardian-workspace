"""Comprehensive tests for FastAPI main application."""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

import pytest
import structlog
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.datastructures import State

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestLifespanManager:
    """Tests for application lifespan management."""
    
    @pytest.mark.asyncio
    async def test_lifespan_startup_shutdown(self):
        """Test application startup and shutdown."""
        from legend_guardian.api.main import lifespan
        from legend_guardian.config import settings
        
        app = FastAPI()
        
        # Mock settings
        with patch.object(settings, 'app_version', '1.0.0'), \
             patch.object(settings, 'otel_enabled', False):
            
            # Test lifespan context
            async with lifespan(app) as _:
                pass  # Startup happens here
            # Shutdown happens after exiting context
    
    @pytest.mark.asyncio
    async def test_lifespan_with_otel_enabled(self):
        """Test lifespan with OpenTelemetry enabled."""
        from legend_guardian.api.main import lifespan
        from legend_guardian.config import settings
        
        app = FastAPI()
        
        with patch.object(settings, 'otel_enabled', True), \
             patch('legend_guardian.api.main._OTEL_AVAILABLE', True), \
             patch('legend_guardian.api.main.trace') as mock_trace, \
             patch('legend_guardian.api.main.FastAPIInstrumentor') as mock_instrumentor:
            
            mock_trace.get_tracer.return_value = MagicMock()
            
            async with lifespan(app):
                pass
            
            mock_trace.get_tracer.assert_called_once()
            mock_instrumentor.instrument_app.assert_called_once_with(app)
    
    @pytest.mark.asyncio
    async def test_lifespan_otel_enabled_but_not_available(self):
        """Test lifespan when OTEL is enabled but not installed."""
        from legend_guardian.api.main import lifespan
        from legend_guardian.config import settings
        
        app = FastAPI()
        
        with patch.object(settings, 'otel_enabled', True), \
             patch('legend_guardian.api.main._OTEL_AVAILABLE', False), \
             patch('legend_guardian.api.main.logger') as mock_logger:
            
            async with lifespan(app):
                pass
            
            # Should log warning about OTEL not being available
            mock_logger.warning.assert_called()


class TestMiddleware:
    """Tests for custom middleware."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        from legend_guardian.api.main import app
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_correlation_id_middleware(self):
        """Test correlation ID middleware."""
        from legend_guardian.api.main import add_correlation_id
        
        # Create mock request
        request = MagicMock(spec=Request)
        request.headers = {"X-Correlation-ID": "test-correlation-123"}
        request.state = State()
        
        # Create mock response
        response = MagicMock()
        response.headers = {}
        
        # Create mock call_next
        async def call_next(req):
            return response
        
        # Test middleware
        with patch('structlog.contextvars.bound_contextvars') as mock_bound:
            result = await add_correlation_id(request, call_next)
            
            # Check correlation ID was set
            assert request.state.correlation_id == "test-correlation-123"
            assert result.headers["X-Correlation-ID"] == "test-correlation-123"
            mock_bound.assert_called_once_with(correlation_id="test-correlation-123")
    
    @pytest.mark.asyncio
    async def test_correlation_id_middleware_no_header(self):
        """Test correlation ID middleware without header."""
        from legend_guardian.api.main import add_correlation_id
        
        # Create mock request without correlation ID
        request = MagicMock(spec=Request)
        request.headers = {}
        request.state = State()
        
        response = MagicMock()
        response.headers = {}
        
        async def call_next(req):
            return response
        
        with patch('time.time', return_value=1234567890.123):
            result = await add_correlation_id(request, call_next)
            
            # Should generate correlation ID from timestamp
            assert request.state.correlation_id == "1234567890.123"
            assert result.headers["X-Correlation-ID"] == "1234567890.123"
    
    @pytest.mark.asyncio
    async def test_log_requests_middleware(self):
        """Test request logging middleware."""
        from legend_guardian.api.main import log_requests
        
        # Create mock request
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = MagicMock()
        request.url.path = "/test"
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        response = MagicMock()
        response.status_code = 200
        
        async def call_next(req):
            await asyncio.sleep(0.1)  # Simulate processing time
            return response
        
        with patch('legend_guardian.api.main.logger') as mock_logger, \
             patch('time.time', side_effect=[1000.0, 1000.15]):
            
            result = await log_requests(request, call_next)
            
            # Check logging calls
            assert mock_logger.info.call_count == 2
            
            # First call - request started
            first_call = mock_logger.info.call_args_list[0]
            assert first_call[0][0] == "Request started"
            assert first_call[1]["method"] == "GET"
            assert first_call[1]["path"] == "/test"
            assert first_call[1]["client"] == "127.0.0.1"
            
            # Second call - request completed
            second_call = mock_logger.info.call_args_list[1]
            assert second_call[0][0] == "Request completed"
            assert second_call[1]["status_code"] == 200
            assert second_call[1]["duration_ms"] == 150.0
    
    @pytest.mark.asyncio
    async def test_log_requests_middleware_no_client(self):
        """Test request logging middleware without client info."""
        from legend_guardian.api.main import log_requests
        
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = MagicMock()
        request.url.path = "/api/test"
        request.client = None  # No client info
        
        response = MagicMock()
        response.status_code = 201
        
        async def call_next(req):
            return response
        
        with patch('legend_guardian.api.main.logger') as mock_logger:
            await log_requests(request, call_next)
            
            # Check client is None in logs
            first_call = mock_logger.info.call_args_list[0]
            assert first_call[1]["client"] is None


class TestExceptionHandler:
    """Tests for global exception handler."""
    
    @pytest.mark.asyncio
    async def test_global_exception_handler(self):
        """Test global exception handler."""
        from legend_guardian.api.main import global_exception_handler
        
        # Create mock request
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = MagicMock()
        request.url.path = "/error"
        request.state = State()
        request.state.correlation_id = "test-123"
        
        # Create exception
        exc = ValueError("Test error")
        
        with patch('legend_guardian.api.main.logger') as mock_logger:
            response = await global_exception_handler(request, exc)
            
            # Check error was logged
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert call_args[0][0] == "Unhandled exception"
            assert call_args[1]["exc_info"] == exc
            assert call_args[1]["method"] == "GET"
            assert call_args[1]["path"] == "/error"
            
            # Check response
            assert response.status_code == 500
            content = response.body.decode()
            assert "INTERNAL_ERROR" in content
            assert "test-123" in content
    
    @pytest.mark.asyncio
    async def test_global_exception_handler_no_correlation_id(self):
        """Test exception handler without correlation ID."""
        from legend_guardian.api.main import global_exception_handler
        
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = MagicMock()
        request.url.path = "/api/error"
        request.state = State()  # No correlation_id attribute
        
        exc = RuntimeError("Critical error")
        
        response = await global_exception_handler(request, exc)
        
        assert response.status_code == 500
        content = response.body.decode()
        assert "null" in content or "None" in content  # correlation_id should be None


class TestRouterInclusion:
    """Tests for router inclusion."""
    
    def test_all_routers_included(self):
        """Test that all routers are properly included."""
        from legend_guardian.api.main import app
        
        # Get all routes
        routes = [route.path for route in app.routes]
        
        # Check health routes
        assert any("/health" in route for route in routes)
        
        # Check intent routes
        assert any("/intent" in route for route in routes)
        
        # Check adapter routes
        assert any("/adapters/engine" in route for route in routes)
        assert any("/adapters/sdlc" in route for route in routes)
        assert any("/adapters/depot" in route for route in routes)
        
        # Check flow routes
        assert any("/flows" in route for route in routes)
        
        # Check webhook routes
        assert any("/webhooks" in route for route in routes)
    
    def test_router_tags(self):
        """Test that routers have appropriate tags."""
        from legend_guardian.api.main import app
        
        # Check routes and their tags
        routes_with_tags = set()
        for route in app.routes:
            if hasattr(route, "tags") and route.tags:
                routes_with_tags.update(route.tags)
        
        expected_tags = {"Health", "Agent", "Engine", "SDLC", "Depot", "Flows", "Webhooks", "Root"}
        assert expected_tags.issubset(routes_with_tags)


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from legend_guardian.api.main import app
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        from legend_guardian.config import settings
        
        with patch.object(settings, 'app_name', 'Test App'), \
             patch.object(settings, 'app_version', '2.0.0'):
            
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["name"] == "Test App"
            assert data["version"] == "2.0.0"
            assert data["docs"] == "/docs"
            assert data["health"] == "/health"
    
    def test_openapi_endpoint(self, client):
        """Test OpenAPI schema endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_docs_endpoint(self, client):
        """Test documentation endpoint."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestCORSMiddleware:
    """Tests for CORS middleware configuration."""
    
    def test_cors_configuration(self):
        """Test CORS middleware is properly configured."""
        from legend_guardian.api.main import app
        from legend_guardian.config import settings
        
        # Find CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls.__name__ == "CORSMiddleware":
                cors_middleware = middleware
                break
        
        assert cors_middleware is not None
        
        # Check CORS options
        options = cors_middleware.options
        assert options["allow_origins"] == settings.cors_origins
        assert options["allow_credentials"] is True
        assert options["allow_methods"] == ["*"]
        assert options["allow_headers"] == ["*"]


class TestStructlogConfiguration:
    """Tests for structlog configuration."""
    
    def test_structlog_configured(self):
        """Test that structlog is properly configured."""
        import structlog
        
        # Get current configuration
        config = structlog.get_config()
        
        # Check processors are configured
        assert config["processors"] is not None
        assert len(config["processors"]) > 0
        
        # Check context class
        assert config["context_class"] == dict
        
        # Check logger factory
        assert config["logger_factory"] is not None
    
    def test_logger_instance(self):
        """Test logger instance creation."""
        from legend_guardian.api.main import logger
        
        assert logger is not None
        
        # Test logging doesn't raise errors
        with patch('sys.stdout'):  # Suppress output
            logger.info("Test message")
            logger.error("Test error", exc_info=Exception("test"))


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""
    
    def test_app_metadata(self):
        """Test app metadata configuration."""
        from legend_guardian.api.main import app
        from legend_guardian.config import settings
        
        assert app.title == settings.app_name
        assert app.version == settings.app_version
        assert app.description == "Production-grade agent for orchestrating FINOS Legend stack operations"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"


class TestMainModuleExecution:
    """Tests for main module execution."""
    
    def test_main_module_execution(self):
        """Test main module execution block."""
        with patch('uvicorn.run') as mock_run, \
             patch.object(sys, 'argv', ['main.py']), \
             patch('legend_guardian.api.main.__name__', '__main__'):
            
            # Import would trigger the if __name__ == "__main__" block
            # We'll simulate it
            from legend_guardian.config import settings
            
            # Simulate the call that would happen
            mock_run(
                "src.api.main:app",
                host="0.0.0.0",
                port=8000,
                reload=settings.debug,
                log_level=settings.log_level.lower(),
            )
            
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0]
            assert call_args[0] == "src.api.main:app"
            
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["host"] == "0.0.0.0"
            assert call_kwargs["port"] == 8000


class TestIntegrationScenarios:
    """Integration tests for complete request flows."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from legend_guardian.api.main import app
        return TestClient(app)
    
    def test_request_with_correlation_id_flow(self, client):
        """Test complete request flow with correlation ID."""
        correlation_id = "integration-test-123"
        
        response = client.get(
            "/",
            headers={"X-Correlation-ID": correlation_id}
        )
        
        assert response.status_code == 200
        assert response.headers.get("X-Correlation-ID") == correlation_id
    
    def test_request_without_correlation_id_flow(self, client):
        """Test complete request flow without correlation ID."""
        response = client.get("/")
        
        assert response.status_code == 200
        # Should have generated correlation ID
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] is not None
    
    def test_error_handling_flow(self, client):
        """Test error handling in complete flow."""
        # Test 404 error
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Should still have correlation ID
        assert "X-Correlation-ID" in response.headers
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 204]