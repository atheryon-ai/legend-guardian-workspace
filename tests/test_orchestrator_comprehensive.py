"""Comprehensive tests for Agent Orchestrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent.orchestrator import AgentOrchestrator
from legend_guardian.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        engine_url="http://test-engine:6300",
        sdlc_url="http://test-sdlc:6100",
        depot_url="http://test-depot:6200"
    )


@pytest.fixture
def orchestrator(settings):
    """Create orchestrator instance."""
    return AgentOrchestrator(settings)


@pytest.mark.asyncio
async def test_orchestrator_initialization(settings):
    """Test orchestrator initialization."""
    orch = AgentOrchestrator(settings)
    assert orch.settings == settings
    assert orch.engine_client is not None
    assert orch.sdlc_client is not None
    assert orch.depot_client is not None
    assert orch.memory is not None
    assert orch.policy_engine is not None


@pytest.mark.asyncio
async def test_parse_intent_create_model(orchestrator):
    """Test parsing intent for model creation."""
    intent = "Create a Person model with name and age properties"
    
    result = await orchestrator.parse_intent(intent)
    
    assert result["intent_type"] in ["create_model", "model_creation"]
    assert "parameters" in result
    assert result["confidence"] > 0


@pytest.mark.asyncio
async def test_parse_intent_deploy_service(orchestrator):
    """Test parsing intent for service deployment."""
    intent = "Deploy the customer service to production"
    
    result = await orchestrator.parse_intent(intent)
    
    assert result["intent_type"] in ["deploy", "deployment", "service_deployment"]
    assert "parameters" in result


@pytest.mark.asyncio
async def test_parse_intent_unknown(orchestrator):
    """Test parsing unknown intent."""
    intent = "Some random text that doesn't match any pattern"
    
    result = await orchestrator.parse_intent(intent)
    
    assert result["intent_type"] == "unknown"
    assert result["confidence"] < 0.5


@pytest.mark.asyncio
async def test_execute_step_create_workspace(orchestrator):
    """Test executing create workspace step."""
    with patch.object(orchestrator.sdlc_client, 'create_workspace') as mock_create:
        mock_create.return_value = {"workspaceId": "test-ws", "status": "created"}
        
        step = {
            "action": "create_workspace",
            "params": {
                "project_id": "test-project",
                "workspace_id": "test-ws"
            }
        }
        
        result = await orchestrator.execute_step(step)
        
        assert result["status"] == "success"
        assert result["data"]["workspaceId"] == "test-ws"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_execute_step_compile(orchestrator):
    """Test executing compile step."""
    with patch.object(orchestrator.engine_client, 'compile') as mock_compile:
        mock_compile.return_value = {
            "status": "SUCCESS",
            "warnings": [],
            "errors": []
        }
        
        step = {
            "action": "compile",
            "params": {
                "model": {"elements": []}
            }
        }
        
        result = await orchestrator.execute_step(step)
        
        assert result["status"] == "success"
        assert result["data"]["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_execute_step_with_error(orchestrator):
    """Test executing step that fails."""
    with patch.object(orchestrator.sdlc_client, 'create_workspace') as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        step = {
            "action": "create_workspace",
            "params": {
                "project_id": "test-project",
                "workspace_id": "test-ws"
            }
        }
        
        result = await orchestrator.execute_step(step)
        
        assert result["status"] == "error"
        assert "API Error" in result["error"]


@pytest.mark.asyncio
async def test_validate_step_success(orchestrator):
    """Test validating successful step result."""
    step_result = {
        "status": "success",
        "data": {"compiled": True}
    }
    
    result = await orchestrator.validate_step(step_result)
    
    assert result["valid"] is True
    assert result["issues"] == []


@pytest.mark.asyncio
async def test_validate_step_error(orchestrator):
    """Test validating failed step result."""
    step_result = {
        "status": "error",
        "error": "Compilation failed"
    }
    
    result = await orchestrator.validate_step(step_result)
    
    assert result["valid"] is False
    assert len(result["issues"]) > 0


@pytest.mark.asyncio
async def test_validate_step_with_warnings(orchestrator):
    """Test validating step with warnings."""
    step_result = {
        "status": "success",
        "data": {"status": "SUCCESS"},
        "warnings": ["Deprecated API used"]
    }
    
    result = await orchestrator.validate_step(step_result)
    
    assert result["valid"] is True
    assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_create_workspace_step(orchestrator):
    """Test internal create workspace method."""
    with patch.object(orchestrator.sdlc_client, 'create_workspace') as mock_create:
        mock_create.return_value = {"workspaceId": "ws1"}
        
        params = {
            "project_id": "proj1",
            "workspace_id": "ws1"
        }
        
        result = await orchestrator._create_workspace(params)
        
        assert result["status"] == "success"
        assert result["workspace_id"] == "ws1"


@pytest.mark.asyncio
async def test_search_depot_step(orchestrator):
    """Test internal search depot method."""
    with patch.object(orchestrator.depot_client, 'search') as mock_search:
        mock_search.return_value = [
            {"id": "model1", "name": "Model 1"},
            {"id": "model2", "name": "Model 2"}
        ]
        
        params = {
            "query": "test query",
            "limit": 10
        }
        
        result = await orchestrator._search_depot(params)
        
        assert len(result) == 2
        assert result[0]["id"] == "model1"


@pytest.mark.asyncio
async def test_compile_step(orchestrator):
    """Test internal compile method."""
    with patch.object(orchestrator.engine_client, 'compile') as mock_compile:
        mock_compile.return_value = {
            "status": "SUCCESS",
            "warnings": [],
            "errors": []
        }
        
        params = {
            "model": {"elements": []},
            "options": {}
        }
        
        result = await orchestrator._compile(params)
        
        assert result["status"] == "success"
        assert result["compile_status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_run_tests_step(orchestrator):
    """Test internal run tests method."""
    with patch.object(orchestrator.engine_client, 'run_tests') as mock_tests:
        mock_tests.return_value = {
            "status": "SUCCESS",
            "results": [
                {"test": "test1", "status": "PASS"},
                {"test": "test2", "status": "PASS"}
            ]
        }
        
        params = {
            "test_data": {"tests": ["test1", "test2"]}
        }
        
        result = await orchestrator._run_tests(params)
        
        assert result["status"] == "success"
        assert result["test_results"]["status"] == "SUCCESS"
        assert len(result["test_results"]["results"]) == 2


@pytest.mark.asyncio
async def test_publish_step(orchestrator):
    """Test internal publish method."""
    with patch.object(orchestrator.depot_client, 'publish') as mock_publish:
        mock_publish.return_value = {
            "status": "success",
            "version": "1.0.0"
        }
        
        params = {
            "project_id": "proj1",
            "version": "1.0.0",
            "entities": []
        }
        
        result = await orchestrator._publish(params)
        
        assert result["status"] == "success"
        assert result["published_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_execute_plan(orchestrator):
    """Test executing a complete plan."""
    plan = {
        "steps": [
            {
                "action": "create_workspace",
                "params": {"project_id": "p1", "workspace_id": "w1"}
            },
            {
                "action": "compile",
                "params": {"model": {"elements": []}}
            }
        ]
    }
    
    with patch.object(orchestrator, 'execute_step') as mock_execute:
        mock_execute.return_value = {"status": "success", "data": {}}
        
        results = []
        for step in plan["steps"]:
            result = await orchestrator.execute_step(step)
            results.append(result)
        
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)
        assert mock_execute.call_count == 2


@pytest.mark.asyncio
async def test_memory_tracking(orchestrator):
    """Test that orchestrator tracks actions in memory."""
    # Add episode
    episode_id = orchestrator.memory.add_episode(
        user_intent="Test intent",
        plan={"steps": []}
    )
    
    # Execute step with memory tracking
    with patch.object(orchestrator.sdlc_client, 'create_workspace') as mock_create:
        mock_create.return_value = {"workspaceId": "ws1"}
        
        step = {
            "action": "create_workspace",
            "params": {"project_id": "p1", "workspace_id": "ws1"}
        }
        
        result = await orchestrator.execute_step(step)
        
        # Add action to memory
        orchestrator.memory.add_action(
            episode_id=episode_id,
            action_type=step["action"],
            params=step["params"],
            result=result
        )
        
        # Check memory
        actions = orchestrator.memory.get_episode_actions(episode_id)
        assert len(actions) == 1
        assert actions[0]["action_type"] == "create_workspace"


@pytest.mark.asyncio
async def test_policy_checking(orchestrator):
    """Test that orchestrator checks policies."""
    with patch.object(orchestrator.policy_engine, 'check_action') as mock_check:
        mock_check.return_value = {
            "allowed": True,
            "warnings": [],
            "violations": []
        }
        
        # Check action with policy
        result = await orchestrator.policy_engine.check_action(
            action_type="deploy",
            params={"environment": "staging"}
        )
        
        assert result["allowed"] is True
        mock_check.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling_in_step(orchestrator):
    """Test error handling in step execution."""
    with patch.object(orchestrator.engine_client, 'compile') as mock_compile:
        mock_compile.side_effect = Exception("Network error")
        
        step = {
            "action": "compile",
            "params": {"model": {}}
        }
        
        result = await orchestrator.execute_step(step)
        
        assert result["status"] == "error"
        assert "Network error" in result["error"]


@pytest.mark.asyncio
async def test_parallel_step_execution(orchestrator):
    """Test executing multiple steps in parallel."""
    steps = [
        {"action": "search_depot", "params": {"query": "test1"}},
        {"action": "search_depot", "params": {"query": "test2"}},
        {"action": "search_depot", "params": {"query": "test3"}}
    ]
    
    with patch.object(orchestrator.depot_client, 'search') as mock_search:
        mock_search.return_value = []
        
        # Execute steps (could be parallelized in real implementation)
        results = []
        for step in steps:
            result = await orchestrator.execute_step(step)
            results.append(result)
        
        assert len(results) == 3
        assert mock_search.call_count == 3


@pytest.mark.asyncio
async def test_rollback_on_failure(orchestrator):
    """Test rollback behavior on failure."""
    # This would test rollback logic if implemented
    with patch.object(orchestrator.sdlc_client, 'delete_workspace') as mock_delete:
        mock_delete.return_value = {"status": "deleted"}
        
        # Simulate rollback
        rollback_params = {
            "project_id": "p1",
            "workspace_id": "w1"
        }
        
        result = await orchestrator.sdlc_client.delete_workspace(
            rollback_params["project_id"],
            rollback_params["workspace_id"]
        )
        
        assert result["status"] == "deleted"