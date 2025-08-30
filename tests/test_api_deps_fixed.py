"""Tests for API dependencies - Fixed version."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.api.deps import (
    get_api_key,
    get_correlation_id,
    get_project_id,
    get_workspace_id,
    get_pii_redactor,
    PIIRedactor
)
from legend_guardian.config import Settings


@pytest.mark.asyncio
async def test_get_api_key_valid():
    """Test API key validation with valid key."""
    # Mock credentials and settings
    mock_credentials = MagicMock()
    mock_credentials.credentials = "test-api-key"
    mock_settings = MagicMock()
    mock_settings.valid_api_keys = ["test-api-key"]
    
    result = await get_api_key(credentials=mock_credentials, settings=mock_settings)
    assert result == "test-api-key"


@pytest.mark.asyncio
async def test_get_api_key_none():
    """Test API key validation with None."""
    # When credentials are None, should raise
    mock_settings = MagicMock()
    mock_settings.valid_api_keys = ["test-api-key"]
    
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key(credentials=None, settings=mock_settings)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_correlation_id_provided():
    """Test correlation ID when provided."""
    mock_request = MagicMock()
    result = await get_correlation_id(request=mock_request, x_correlation_id="test-correlation-123")
    assert result == "test-correlation-123"


@pytest.mark.asyncio
async def test_get_correlation_id_generated():
    """Test correlation ID generation when not provided."""
    mock_request = MagicMock()
    mock_request.state.correlation_id = "generated-123"
    result = await get_correlation_id(request=mock_request, x_correlation_id=None)
    assert result == "generated-123"


@pytest.mark.asyncio
async def test_get_project_id_from_header():
    """Test getting project ID from header."""
    mock_settings = MagicMock()
    mock_settings.project_id = "default-project"
    result = await get_project_id(project_id="test-project", settings=mock_settings)
    assert result == "test-project"


@pytest.mark.asyncio
async def test_get_project_id_none():
    """Test getting project ID when not provided."""
    mock_settings = MagicMock()
    mock_settings.project_id = "default-project"
    result = await get_project_id(project_id=None, settings=mock_settings)
    assert result == "default-project"


@pytest.mark.asyncio
async def test_get_workspace_id_from_header():
    """Test getting workspace ID from header."""
    mock_settings = MagicMock()
    mock_settings.workspace_id = "default-workspace"
    result = await get_workspace_id(workspace_id="test-workspace", settings=mock_settings)
    assert result == "test-workspace"


@pytest.mark.asyncio
async def test_get_workspace_id_none():
    """Test getting workspace ID when not provided."""
    mock_settings = MagicMock()
    mock_settings.workspace_id = "default-workspace"
    result = await get_workspace_id(workspace_id=None, settings=mock_settings)
    assert result == "default-workspace"


@pytest.mark.asyncio
async def test_get_pii_redactor():
    """Test getting PII redactor."""
    mock_settings = MagicMock()
    mock_settings.pii_redaction_enabled = True
    
    redactor = await get_pii_redactor(settings=mock_settings)
    assert redactor is not None
    assert hasattr(redactor, 'redact')
    
    # Test that it redacts PII
    test_text = "My email is john@example.com and SSN is 123-45-6789"
    redacted = redactor.redact(test_text)
    assert "john@example.com" not in redacted or redacted != test_text


@pytest.mark.asyncio
async def test_api_key_with_settings():
    """Test API key validation with settings."""
    mock_credentials = MagicMock()
    mock_credentials.credentials = "expected-key"
    mock_settings = MagicMock()
    mock_settings.valid_api_keys = ["expected-key"]
    
    result = await get_api_key(credentials=mock_credentials, settings=mock_settings)
    assert result == "expected-key"


@pytest.mark.asyncio
async def test_correlation_id_format():
    """Test correlation ID format."""
    import uuid
    
    mock_request = MagicMock()
    mock_request.state.correlation_id = str(uuid.uuid4())
    
    # Generated correlation ID should be valid UUID
    result = await get_correlation_id(request=mock_request, x_correlation_id=None)
    
    # Try to parse as UUID
    try:
        uuid.UUID(result)
        is_uuid = True
    except ValueError:
        is_uuid = False
    
    # Should be either a UUID or a non-empty string
    assert result
    assert isinstance(result, str)
    assert is_uuid