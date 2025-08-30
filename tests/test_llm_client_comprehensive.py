"""Comprehensive tests for LLM Client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent.llm_client import LLMClient


@pytest.fixture
def llm_client():
    """Create LLM client instance."""
    return LLMClient(provider="openai", model="gpt-4")


def test_llm_client_initialization():
    """Test LLM client initialization."""
    client = LLMClient(provider="openai", model="gpt-4")
    assert client.provider == "openai"
    assert client.model == "gpt-4"


def test_llm_client_default_initialization():
    """Test LLM client with default values."""
    client = LLMClient()
    assert client.provider == "openai"
    assert client.model == "gpt-4"


def test_llm_client_custom_provider():
    """Test LLM client with custom provider."""
    client = LLMClient(provider="anthropic", model="claude-3")
    assert client.provider == "anthropic"
    assert client.model == "claude-3"


@pytest.mark.asyncio
async def test_parse_intent_create_workspace(llm_client):
    """Test parsing intent for creating workspace."""
    result = await llm_client.parse_intent("Create a new workspace")
    
    assert len(result) > 0
    assert result[0]["action"] == "sdlc.create_workspace"


@pytest.mark.asyncio
async def test_parse_intent_compile(llm_client):
    """Test parsing intent for compile action."""
    result = await llm_client.parse_intent("Compile the model")
    
    assert len(result) > 0
    assert result[0]["action"] == "engine.compile"


@pytest.mark.asyncio
async def test_parse_intent_run_tests(llm_client):
    """Test parsing intent for running tests."""
    result = await llm_client.parse_intent("Run all tests")
    
    assert len(result) > 0
    assert result[0]["action"] == "engine.run_tests"


@pytest.mark.asyncio
async def test_parse_intent_publish(llm_client):
    """Test parsing intent for publishing."""
    result = await llm_client.parse_intent("Publish to depot")
    
    assert len(result) > 0
    # The implementation returns engine.deploy for publish
    assert result[0]["action"] == "engine.deploy"


@pytest.mark.asyncio
async def test_parse_intent_deploy(llm_client):
    """Test parsing intent for deployment."""
    result = await llm_client.parse_intent("Deploy the service")
    
    assert len(result) > 0
    assert result[0]["action"] == "engine.deploy"


@pytest.mark.asyncio
async def test_parse_intent_rollback(llm_client):
    """Test parsing intent for rollback."""
    result = await llm_client.parse_intent("Rollback to previous version")
    
    assert len(result) > 0
    # The implementation returns sdlc.open_review for rollback
    assert result[0]["action"] == "sdlc.open_review"


@pytest.mark.asyncio
async def test_parse_intent_multiple_actions(llm_client):
    """Test parsing intent with multiple actions."""
    result = await llm_client.parse_intent("Create a workspace and compile")
    
    assert len(result) == 2
    assert result[0]["action"] == "sdlc.create_workspace"
    assert result[1]["action"] == "engine.compile"


@pytest.mark.asyncio
async def test_parse_intent_with_context(llm_client):
    """Test parsing intent with context."""
    context = {"project": "test-project", "workspace": "test-workspace"}
    result = await llm_client.parse_intent("Compile the model", context)
    
    assert len(result) > 0
    assert result[0]["action"] == "engine.compile"


@pytest.mark.asyncio
async def test_parse_intent_empty_prompt(llm_client):
    """Test parsing intent with empty prompt."""
    result = await llm_client.parse_intent("")
    
    assert result == []


@pytest.mark.asyncio
async def test_parse_intent_unknown_action(llm_client):
    """Test parsing intent with unknown action."""
    result = await llm_client.parse_intent("Do something random")
    
    # Should return empty or minimal result for unknown actions
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_parse_intent_case_insensitive(llm_client):
    """Test that intent parsing is case insensitive."""
    result1 = await llm_client.parse_intent("CREATE a WORKSPACE")
    result2 = await llm_client.parse_intent("create a workspace")
    
    assert result1 == result2


@pytest.mark.asyncio
async def test_parse_intent_with_special_chars(llm_client):
    """Test parsing intent with special characters."""
    result = await llm_client.parse_intent("Create workspace @#$%")
    
    assert len(result) > 0
    assert result[0]["action"] == "sdlc.create_workspace"


@pytest.mark.asyncio
async def test_parse_intent_complex_prompt(llm_client):
    """Test parsing complex prompt."""
    prompt = """
    I need to create a new workspace for our trading models,
    then compile everything and run the tests. If tests pass,
    publish to depot.
    """
    result = await llm_client.parse_intent(prompt)
    
    # Should identify multiple actions
    assert len(result) >= 3
    actions = [step["action"] for step in result]
    assert "sdlc.create_workspace" in actions
    assert "engine.compile" in actions
    assert "engine.run_tests" in actions


@pytest.mark.asyncio
async def test_parse_intent_with_params(llm_client):
    """Test that parse_intent includes params dict."""
    result = await llm_client.parse_intent("Create workspace")
    
    assert len(result) > 0
    assert "params" in result[0]
    assert isinstance(result[0]["params"], dict)


def test_llm_client_provider_variations():
    """Test different provider configurations."""
    providers = [
        ("openai", "gpt-4"),
        ("anthropic", "claude-3"),
        ("ollama", "llama2"),
        ("custom", "custom-model")
    ]
    
    for provider, model in providers:
        client = LLMClient(provider=provider, model=model)
        assert client.provider == provider
        assert client.model == model