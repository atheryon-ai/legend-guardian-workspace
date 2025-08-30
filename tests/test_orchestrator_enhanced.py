"""Enhanced tests for Agent Orchestrator with comprehensive coverage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from legend_guardian.agent.orchestrator import AgentOrchestrator
from legend_guardian.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings(
        engine_url="http://engine:6300",
        sdlc_url="http://sdlc:6100",
        depot_url="http://depot:6200",
        studio_url="http://studio:9000",
        agent_model="gpt-4",
        project_id="test-project",
        workspace_id="test-workspace"
    )


@pytest.fixture
def orchestrator(settings):
    """Create orchestrator instance."""
    return AgentOrchestrator(settings)


class TestParseIntent:
    """Tests for parse_intent method."""
    
    @pytest.mark.asyncio
    async def test_parse_intent_with_llm(self, orchestrator):
        """Test intent parsing with LLM."""
        expected_steps = [
            {"action": "create_workspace", "params": {"workspace_id": "test"}},
            {"action": "compile", "params": {}}
        ]
        
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = expected_steps
            with patch.object(orchestrator.policy_engine, 'validate_plan', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = expected_steps
                
                result = await orchestrator.parse_intent("Create a workspace and compile")
                
                assert result == expected_steps
                mock_parse.assert_called_once()
                mock_validate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_intent_fallback_create(self, orchestrator):
        """Test fallback parsing for create intent."""
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.side_effect = Exception("LLM error")
            
            result = await orchestrator.parse_intent("create a trade model")
            
            assert len(result) > 0
            assert result[0]["action"] == "create_model"
            assert "Trade" in str(result[0]["params"])  # Trade is recognized by _extract_model_params
    
    @pytest.mark.asyncio
    async def test_parse_intent_fallback_compile(self, orchestrator):
        """Test fallback parsing for compile intent."""
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.side_effect = Exception("LLM error")
            
            result = await orchestrator.parse_intent("compile the model")
            
            assert len(result) > 0
            assert result[0]["action"] == "compile"
    
    @pytest.mark.asyncio
    async def test_parse_intent_with_context(self, orchestrator):
        """Test intent parsing with context."""
        context = {"current_model": "Trade", "workspace": "test"}
        expected_steps = [{"action": "compile", "params": {"model": "Trade"}}]
        
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = expected_steps
            with patch.object(orchestrator.policy_engine, 'validate_plan', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = expected_steps
                
                result = await orchestrator.parse_intent("compile", context)
                
                assert result == expected_steps
                mock_parse.assert_called_with("compile", context)


class TestExecuteStep:
    """Tests for execute_step method."""
    
    @pytest.mark.asyncio
    async def test_execute_create_workspace(self, orchestrator):
        """Test executing create workspace step."""
        action = "create_workspace"
        params = {"workspace_id": "test-ws", "project_id": "test-proj"}
        
        with patch.object(orchestrator, '_create_workspace', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"workspaceId": "test-ws", "projectId": "test-proj", "status": "created"}
            
            result = await orchestrator.execute_step(action, params)
            
            assert "workspaceId" in result
            mock_create.assert_called_once_with(params)
    
    @pytest.mark.asyncio
    async def test_execute_create_model(self, orchestrator):
        """Test executing create model step."""
        action = "create_model"
        params = {"name": "Person", "csv_data": "name,age\nJohn,30"}
        
        with patch.object(orchestrator, '_create_model', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"model": "Person", "pure": "Class model::Person {}"}
            
            result = await orchestrator.execute_step(action, params)
            
            assert "model" in result
            mock_create.assert_called_once_with(params)
    
    @pytest.mark.asyncio
    async def test_execute_compile(self, orchestrator):
        """Test executing compile step."""
        action = "compile"
        params = {"project_id": "test-project", "workspace_id": "test-workspace"}
        
        with patch.object(orchestrator, '_compile', new_callable=AsyncMock) as mock_compile:
            mock_compile.return_value = {"status": "success", "errors": [], "warnings": []}
            
            result = await orchestrator.execute_step(action, params)
            
            assert result["status"] == "success"
            mock_compile.assert_called_once_with(params)
    
    @pytest.mark.asyncio
    async def test_execute_run_tests(self, orchestrator):
        """Test executing run tests step."""
        action = "run_tests"
        params = {"test_suite": "all"}
        
        with patch.object(orchestrator, '_run_tests', new_callable=AsyncMock) as mock_tests:
            mock_tests.return_value = {"passed": True, "results": []}
            
            result = await orchestrator.execute_step(action, params)
            
            assert result["passed"] is True
            mock_tests.assert_called_once_with(params)
    
    @pytest.mark.asyncio
    async def test_execute_unknown_action(self, orchestrator):
        """Test executing unknown action."""
        action = "unknown_action"
        params = {}
        
        with pytest.raises(ValueError) as exc_info:
            await orchestrator.execute_step(action, params)
        
        assert "Unknown action" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_with_validation(self, orchestrator):
        """Test step execution with validation."""
        action = "compile"
        params = {"project_id": "test-project", "workspace_id": "test-workspace"}
        
        with patch.object(orchestrator.policy_engine, 'check_action', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = None  # No exception means validation passed
            with patch.object(orchestrator, '_compile', new_callable=AsyncMock) as mock_compile:
                mock_compile.return_value = {"status": "success", "errors": [], "warnings": []}
                
                result = await orchestrator.execute_step(action, params)
                
                mock_check.assert_called_once_with(action, params)
                assert result["status"] == "success"


class TestWorkspaceOperations:
    """Tests for workspace-related operations."""
    
    @pytest.mark.asyncio
    async def test_create_workspace(self, orchestrator):
        """Test workspace creation."""
        params = {
            "workspace_id": "test-workspace",
            "project_id": "test-project"
        }
        
        with patch.object(orchestrator.sdlc_client, 'create_workspace', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {
                "workspaceId": "test-workspace",
                "projectId": "test-project"
            }
            
            result = await orchestrator._create_workspace(params)
            
            # The _create_workspace method directly returns the SDLC client result
            assert result["workspaceId"] == "test-workspace"
            assert result["projectId"] == "test-project"
            mock_create.assert_called_once_with(
                project_id="test-project",
                workspace_id="test-workspace"
            )
    
    @pytest.mark.asyncio
    async def test_create_workspace_error(self, orchestrator):
        """Test workspace creation error handling."""
        params = {"workspace_id": "test", "project_id": "test-project"}
        
        with patch.object(orchestrator.sdlc_client, 'create_workspace', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API error")
            
            # The method doesn't handle exceptions, so it should raise
            with pytest.raises(Exception) as exc_info:
                await orchestrator._create_workspace(params)
            
            assert "API error" in str(exc_info.value)


class TestModelOperations:
    """Tests for model-related operations."""
    
    @pytest.mark.asyncio
    async def test_create_model(self, orchestrator):
        """Test model creation."""
        params = {
            "name": "Person",
            "csv_data": "name,age\nJohn,30\nJane,25"
        }
        
        with patch.object(orchestrator.sdlc_client, 'upsert_entities', new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"status": "success"}
            
            result = await orchestrator._create_model(params)
            
            assert "model" in result
            assert "Person" in result["model"]
            assert "pure" in result
            mock_upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_compile_model(self, orchestrator):
        """Test model compilation."""
        params = {"project_id": "test-project", "workspace_id": "test-workspace"}
        
        with patch.object(orchestrator.engine_client, 'compile', new_callable=AsyncMock) as mock_compile:
            mock_compile.return_value = {
                "status": "success",
                "errors": [],
                "warnings": []
            }
            with patch.object(orchestrator.sdlc_client, 'get_entities', new_callable=AsyncMock) as mock_get_entities:
                mock_get_entities.return_value = [{
                    "path": "model::Test", 
                    "classifierPath": "meta::pure::metamodel::type::Class",
                    "content": {"name": "Test", "package": "model", "properties": []}
                }]
                with patch.object(orchestrator, '_entities_to_pure', return_value="Class model::Test {}\n") as mock_entities_to_pure:
                    
                    result = await orchestrator._compile(params)
                    assert result["status"] == "success"
                    mock_compile.assert_called_once()
                    mock_entities_to_pure.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transform_schema(self, orchestrator):
        """Test schema transformation."""
        params = {
            "format": "avro",
            "class_path": "model::Person"
        }
        
        with patch.object(orchestrator.engine_client, 'transform_to_schema', new_callable=AsyncMock) as mock_transform:
            mock_transform.return_value = {
                "type": "record",
                "name": "Person",
                "fields": []
            }
            
            result = await orchestrator._transform_schema(params)
            
            assert "schema" in result
            assert "format" in result
            assert result["format"] == "avro"
            mock_transform.assert_called_once_with(
                schema_type="avro",
                class_path="model::Person"
            )


class TestDepotOperations:
    """Tests for depot-related operations."""
    
    @pytest.mark.asyncio
    async def test_search_depot(self, orchestrator):
        """Test depot search."""
        params = {
            "query": "Person",
            "limit": 10
        }
        
        with patch.object(orchestrator.depot_client, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"name": "Person", "version": "1.0.0"},
                {"name": "PersonEntity", "version": "2.0.0"}
            ]
            
            result = await orchestrator._search_depot(params)
            
            assert len(result) == 2
            assert result[0]["name"] == "Person"
            mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_import_model(self, orchestrator):
        """Test model import from depot."""
        params = {
            "depot_project_id": "person-project",
            "version": "1.0.0",
            "entity_paths": ["model::Person"]
        }
        
        with patch.object(orchestrator.depot_client, 'get_latest_version', new_callable=AsyncMock) as mock_version:
            mock_version.return_value = "1.0.0"
            with patch.object(orchestrator.depot_client, 'get_entities', new_callable=AsyncMock) as mock_get_entities:
                mock_get_entities.return_value = [
                    {"path": "model::Person", "classifierPath": "meta::pure::metamodel::type::Class", "content": {}}
                ]
                with patch.object(orchestrator.sdlc_client, 'upsert_entities', new_callable=AsyncMock) as mock_upsert:
                    mock_upsert.return_value = {"status": "success"}
                    
                    result = await orchestrator._import_model(params)
                    
                    assert "imported" in result
                    assert result["imported"] is True
                    assert "count" in result
                    assert "entities" in result
    
    @pytest.mark.asyncio
    async def test_publish_to_depot(self, orchestrator):
        """Test publishing to depot."""
        params = {
            "version": "1.0.0",
            "metadata": {"author": "test"}
        }
        
        with patch.object(orchestrator.depot_client, 'publish', new_callable=AsyncMock) as mock_publish:
            mock_publish.return_value = {
                "status": "published",
                "id": "model-123"
            }
            
            result = await orchestrator._publish(params)
            
            # _publish method returns the depot client result directly
            assert result["status"] == "published"
            assert result["id"] == "model-123"
            mock_publish.assert_called_once_with(
                project_id=orchestrator.settings.project_id,
                version="1.0.0"
            )


class TestTestingOperations:
    """Tests for testing-related operations."""
    
    @pytest.mark.asyncio
    async def test_run_tests(self, orchestrator):
        """Test running tests."""
        params = {
            "test_suite": "all",
            "model": "Person"
        }
        
        with patch.object(orchestrator.engine_client, 'run_tests', new_callable=AsyncMock) as mock_tests:
            mock_tests.return_value = [
                {"passed": True, "name": "test1"},
                {"passed": True, "name": "test2"}
            ]
            
            result = await orchestrator._run_tests(params)
            
            assert result["passed"] is True
            assert "results" in result
            mock_tests.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_tests_with_failures(self, orchestrator):
        """Test running tests with failures."""
        params = {"test_suite": "integration"}
        
        with patch.object(orchestrator.engine_client, 'run_tests', new_callable=AsyncMock) as mock_tests:
            mock_tests.return_value = [
                {"passed": True, "name": "test1"},
                {"passed": False, "name": "test2"},
                {"passed": False, "name": "test3"}
            ]
            
            result = await orchestrator._run_tests(params)
            
            assert result["passed"] is False  # Not all tests passed
            assert "results" in result


class TestValidation:
    """Tests for validation methods."""
    
    @pytest.mark.asyncio
    async def test_validate_step(self, orchestrator):
        """Test step validation."""
        action = "create_model"
        params = {"name": "Person"}
        
        with patch.object(orchestrator.policy_engine, 'check_action') as mock_check:
            mock_check.return_value = None  # No exception means validation passed
            
            result = await orchestrator.validate_step(action, params)
            
            assert result["valid"] is True
            assert result["issues"] == []
            mock_check.assert_called_once_with(action, params)
    
    @pytest.mark.asyncio
    async def test_validate_step_with_issues(self, orchestrator):
        """Test step validation with issues."""
        action = "delete_all"
        params = {}
        
        with patch.object(orchestrator.policy_engine, 'check_action') as mock_check:
            mock_check.side_effect = Exception("Dangerous operation not allowed")
            
            result = await orchestrator.validate_step(action, params)
            
            assert result["valid"] is False
            assert len(result["issues"]) > 0
            assert "Dangerous operation not allowed" in result["issues"][0]


class TestMemoryIntegration:
    """Tests for memory integration."""
    
    @pytest.mark.asyncio
    async def test_memory_storage(self, orchestrator):
        """Test that episodes are stored in memory."""
        prompt = "Create a Person model"
        
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = [{"action": "create_model", "params": {"model_name": "Person"}}]
            with patch.object(orchestrator.policy_engine, 'validate_plan', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = mock_parse.return_value
                
                # Clear memory first
                orchestrator.memory.episodes = []
                
                await orchestrator.parse_intent(prompt)
                
                # Check memory was updated
                episodes = orchestrator.memory.get_recent_episodes(1)
                assert len(episodes) > 0
                assert episodes[0]["prompt"] == prompt


class TestServiceOperations:
    """Tests for service generation operations."""
    
    @pytest.mark.asyncio
    async def test_generate_service(self, orchestrator):
        """Test service generation."""
        params = {
            "path": "test/service",
            "query": "model::all",
            "mapping": "mapping::TestMapping",
            "runtime": "runtime::TestRuntime"
        }
        
        with patch.object(orchestrator.sdlc_client, 'upsert_entities', new_callable=AsyncMock) as mock_upsert:
            mock_upsert.return_value = {"status": "success"}
            
            result = await orchestrator._generate_service(params)
            
            assert "service_path" in result
            assert "service_name" in result
            assert result["status"] == "defined"
            mock_upsert.assert_called_once()


class TestReviewOperations:
    """Tests for review operations."""
    
    @pytest.mark.asyncio
    async def test_open_review(self, orchestrator):
        """Test opening a review."""
        params = {
            "title": "Add Person model",
            "description": "Adding new Person model"
        }
        
        with patch.object(orchestrator.sdlc_client, 'create_review', new_callable=AsyncMock) as mock_review:
            mock_review.return_value = {
                "id": "review-123",
                "web_url": "https://example.com/review/123",
                "state": "opened"
            }
            
            result = await orchestrator._open_review(params)
            
            assert "review_id" in result
            assert "url" in result
            assert "state" in result
            mock_review.assert_called_once()


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_execute_step_with_error(self, orchestrator):
        """Test step execution with error."""
        action = "compile"
        params = {"project_id": "test-project", "workspace_id": "test-workspace"}
        
        with patch.object(orchestrator, '_compile', new_callable=AsyncMock) as mock_compile:
            mock_compile.side_effect = Exception("Compilation failed")
            
            # Since execute_step doesn't handle exceptions, it should raise
            with pytest.raises(Exception) as exc_info:
                await orchestrator.execute_step(action, params)
            
            assert "Compilation failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_parse_intent_error_recovery(self, orchestrator):
        """Test parse intent error recovery."""
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.side_effect = Exception("LLM service down")
            
            # Should fall back to rule-based parsing
            result = await orchestrator.parse_intent("compile the model")
            
            assert len(result) > 0
            assert result[0]["action"] == "compile"


class TestComplexWorkflows:
    """Tests for complex multi-step workflows."""
    
    @pytest.mark.asyncio
    async def test_full_development_workflow(self, orchestrator):
        """Test full development workflow."""
        # Parse complex intent
        prompt = "Create a Person model, compile it, run tests, and publish to depot"
        
        with patch.object(orchestrator.llm_client, 'parse_intent', new_callable=AsyncMock) as mock_parse:
            mock_parse.return_value = [
                {"action": "create_model", "params": {"model_name": "Person"}},
                {"action": "compile", "params": {}},
                {"action": "run_tests", "params": {}},
                {"action": "publish", "params": {}}
            ]
            with patch.object(orchestrator.policy_engine, 'validate_plan', new_callable=AsyncMock) as mock_validate:
                mock_validate.return_value = mock_parse.return_value
                
                plan = await orchestrator.parse_intent(prompt)
                
                assert len(plan) == 4
                assert plan[0]["action"] == "create_model"
                assert plan[-1]["action"] == "publish"
    
    @pytest.mark.asyncio
    async def test_import_and_extend_workflow(self, orchestrator):
        """Test import and extend workflow."""
        # Test importing a model and extending it
        params = {
            "depot_project_id": "base-person",
            "version": "1.0.0",
            "entity_paths": ["model::BasePerson"]
        }
        
        with patch.object(orchestrator.depot_client, 'get_latest_version', new_callable=AsyncMock) as mock_version:
            mock_version.return_value = "1.0.0"
            with patch.object(orchestrator.depot_client, 'get_entities', new_callable=AsyncMock) as mock_get_entities:
                mock_get_entities.return_value = [
                    {"path": "model::BasePerson", "classifierPath": "meta::pure::metamodel::type::Class", "content": {}}
                ]
                with patch.object(orchestrator.sdlc_client, 'upsert_entities', new_callable=AsyncMock) as mock_upsert:
                    mock_upsert.return_value = {"status": "success"}
                    
                    result = await orchestrator._import_model(params)
                    
                    assert "imported" in result
                    assert result["imported"] is True
                    assert "entities" in result
                    assert len(result["entities"]) > 0