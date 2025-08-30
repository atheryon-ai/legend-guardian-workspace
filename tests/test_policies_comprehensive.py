"""Comprehensive tests for Policy Engine."""

import pytest
from unittest.mock import patch, mock_open
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent.policies import PolicyEngine


@pytest.fixture
def policy_engine():
    """Create a policy engine instance."""
    return PolicyEngine()


@pytest.fixture
def custom_policy_engine():
    """Create a policy engine with custom policies."""
    policies = {
        "custom_rule": {
            "type": "action",
            "condition": "action_type == 'custom'",
            "action": "deny",
            "message": "Custom actions not allowed"
        }
    }
    with patch.object(PolicyEngine, '_load_default_policies', return_value=policies):
        return PolicyEngine()


def test_policy_engine_initialization():
    """Test PolicyEngine initialization."""
    engine = PolicyEngine()
    assert engine.policies is not None
    assert isinstance(engine.policies, dict)


def test_load_default_policies(policy_engine):
    """Test loading default policies."""
    # Default policies should be loaded
    assert "pii_detection" in policy_engine.policies
    assert "sql_injection" in policy_engine.policies
    assert "large_batch_operation" in policy_engine.policies
    assert "production_deployment" in policy_engine.policies


def test_load_policies_from_file():
    """Test loading policies from file."""
    test_policies = {
        "test_policy": {
            "type": "data",
            "condition": "test condition",
            "action": "warn",
            "message": "Test warning"
        }
    }
    
    mock_file_content = json.dumps(test_policies)
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        with patch('os.path.exists', return_value=True):
            engine = PolicyEngine(policy_file="test_policies.json")
            
            # Should have both default and custom policies
            assert "test_policy" in engine.policies
            assert "pii_detection" in engine.policies


def test_load_policies_from_invalid_file():
    """Test loading from non-existent file."""
    with patch('os.path.exists', return_value=False):
        # Should not raise error, just use defaults
        engine = PolicyEngine(policy_file="nonexistent.json")
        assert "pii_detection" in engine.policies


def test_load_policies_from_malformed_file():
    """Test loading from malformed JSON file."""
    with patch('builtins.open', mock_open(read_data="invalid json")):
        with patch('os.path.exists', return_value=True):
            # Should not raise error, just use defaults
            engine = PolicyEngine(policy_file="malformed.json")
            assert "pii_detection" in engine.policies


@pytest.mark.asyncio
async def test_check_action_allow(policy_engine):
    """Test checking action that should be allowed."""
    result = await policy_engine.check_action(
        action_type="compile",
        params={"model": "test_model"}
    )
    
    assert result["allowed"] is True
    assert result["warnings"] == []
    assert result["violations"] == []


@pytest.mark.asyncio
async def test_check_action_with_pii(policy_engine):
    """Test checking action with PII data."""
    result = await policy_engine.check_action(
        action_type="create_entity",
        params={
            "entity": {
                "name": "Person",
                "properties": [
                    {"name": "ssn", "type": "String"},
                    {"name": "email", "type": "String"}
                ]
            }
        }
    )
    
    assert result["allowed"] is True  # PII detection is warning only
    assert len(result["warnings"]) > 0
    assert any("PII" in w for w in result["warnings"])


@pytest.mark.asyncio
async def test_check_action_with_sql_injection(policy_engine):
    """Test checking action with potential SQL injection."""
    result = await policy_engine.check_action(
        action_type="execute_query",
        params={
            "query": "SELECT * FROM users WHERE id = ' OR '1'='1"
        }
    )
    
    assert result["allowed"] is False
    assert len(result["violations"]) > 0
    assert any("SQL injection" in v for v in result["violations"])


@pytest.mark.asyncio
async def test_check_action_large_batch(policy_engine):
    """Test checking large batch operation."""
    large_entities = [{"id": i} for i in range(1001)]
    
    result = await policy_engine.check_action(
        action_type="batch_update",
        params={"entities": large_entities}
    )
    
    assert result["allowed"] is True  # Large batch is warning only
    assert len(result["warnings"]) > 0
    assert any("Large batch" in w for w in result["warnings"])


@pytest.mark.asyncio
async def test_check_action_production_deployment(policy_engine):
    """Test checking production deployment."""
    result = await policy_engine.check_action(
        action_type="deploy",
        params={"environment": "production"}
    )
    
    assert result["allowed"] is True  # Production deployment requires confirmation
    assert result.get("requires_confirmation") is True
    assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_check_data_allow(policy_engine):
    """Test checking data that should be allowed."""
    result = await policy_engine.check_data(
        data_type="model",
        content={"name": "TestModel", "properties": []}
    )
    
    assert result["allowed"] is True
    assert result["warnings"] == []


@pytest.mark.asyncio
async def test_check_data_with_sensitive_info(policy_engine):
    """Test checking data with sensitive information."""
    result = await policy_engine.check_data(
        data_type="model",
        content={
            "name": "User",
            "properties": [
                {"name": "password", "type": "String"},
                {"name": "credit_card", "type": "String"}
            ]
        }
    )
    
    assert result["allowed"] is True
    assert len(result["warnings"]) > 0


def test_check_compile_result_success(policy_engine):
    """Test checking successful compile result."""
    compile_result = {
        "status": "SUCCESS",
        "warnings": [],
        "errors": []
    }
    
    result = policy_engine.check_compile_result(compile_result)
    
    assert result["passed"] is True
    assert result["issues"] == []


def test_check_compile_result_with_warnings(policy_engine):
    """Test checking compile result with warnings."""
    compile_result = {
        "status": "SUCCESS",
        "warnings": ["Deprecated function used", "Unused variable"],
        "errors": []
    }
    
    result = policy_engine.check_compile_result(compile_result)
    
    assert result["passed"] is True
    assert len(result["issues"]) == 2
    assert result["severity"] == "warning"


def test_check_compile_result_with_errors(policy_engine):
    """Test checking compile result with errors."""
    compile_result = {
        "status": "FAILURE",
        "warnings": [],
        "errors": ["Syntax error at line 10", "Undefined variable"]
    }
    
    result = policy_engine.check_compile_result(compile_result)
    
    assert result["passed"] is False
    assert len(result["issues"]) == 2
    assert result["severity"] == "error"


def test_check_test_result_all_pass(policy_engine):
    """Test checking test result with all tests passing."""
    test_result = {
        "status": "SUCCESS",
        "tests": [
            {"name": "test1", "status": "PASS"},
            {"name": "test2", "status": "PASS"}
        ]
    }
    
    result = policy_engine.check_test_result(test_result)
    
    assert result["passed"] is True
    assert result["total_tests"] == 2
    assert result["passed_tests"] == 2
    assert result["failed_tests"] == 0


def test_check_test_result_with_failures(policy_engine):
    """Test checking test result with failures."""
    test_result = {
        "status": "FAILURE",
        "tests": [
            {"name": "test1", "status": "PASS"},
            {"name": "test2", "status": "FAIL", "error": "Assertion failed"},
            {"name": "test3", "status": "FAIL", "error": "Timeout"}
        ]
    }
    
    result = policy_engine.check_test_result(test_result)
    
    assert result["passed"] is False
    assert result["total_tests"] == 3
    assert result["passed_tests"] == 1
    assert result["failed_tests"] == 2
    assert len(result["failures"]) == 2


def test_check_deployment_requirements_met(policy_engine):
    """Test checking deployment requirements when all are met."""
    requirements = {
        "tests_passed": True,
        "code_review_approved": True,
        "security_scan_passed": True
    }
    
    result = policy_engine.check_deployment_requirements(requirements)
    
    assert result["can_deploy"] is True
    assert result["missing_requirements"] == []


def test_check_deployment_requirements_missing(policy_engine):
    """Test checking deployment requirements with missing items."""
    requirements = {
        "tests_passed": True,
        "code_review_approved": False,
        "security_scan_passed": False
    }
    
    result = policy_engine.check_deployment_requirements(requirements)
    
    assert result["can_deploy"] is False
    assert "code_review_approved" in result["missing_requirements"]
    assert "security_scan_passed" in result["missing_requirements"]


@pytest.mark.asyncio
async def test_check_action_with_nested_pii(policy_engine):
    """Test PII detection in nested structures."""
    result = await policy_engine.check_action(
        action_type="create",
        params={
            "model": {
                "entities": [
                    {
                        "name": "Customer",
                        "attributes": {
                            "personal": {
                                "ssn": "123-45-6789",
                                "email": "test@example.com"
                            }
                        }
                    }
                ]
            }
        }
    )
    
    assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_check_action_with_complex_sql(policy_engine):
    """Test SQL injection detection with complex queries."""
    result = await policy_engine.check_action(
        action_type="query",
        params={
            "sql": "SELECT * FROM users; DROP TABLE users; --"
        }
    )
    
    assert result["allowed"] is False
    assert any("SQL" in v for v in result["violations"])


@pytest.mark.asyncio
async def test_custom_policy_engine(custom_policy_engine):
    """Test custom policy engine."""
    result = await custom_policy_engine.check_action(
        action_type="custom",
        params={}
    )
    
    assert result["allowed"] is False
    assert any("Custom actions not allowed" in v for v in result["violations"])


def test_add_policy_runtime(policy_engine):
    """Test adding policy at runtime."""
    new_policy = {
        "type": "action",
        "condition": "action_type == 'restricted'",
        "action": "deny",
        "message": "Restricted action"
    }
    
    policy_engine.add_policy("runtime_policy", new_policy)
    assert "runtime_policy" in policy_engine.policies


def test_remove_policy_runtime(policy_engine):
    """Test removing policy at runtime."""
    policy_engine.remove_policy("sql_injection")
    assert "sql_injection" not in policy_engine.policies


def test_get_policy_summary(policy_engine):
    """Test getting policy summary."""
    summary = policy_engine.get_policy_summary()
    
    assert "total_policies" in summary
    assert "action_policies" in summary
    assert "data_policies" in summary
    assert summary["total_policies"] > 0


@pytest.mark.asyncio
async def test_batch_check_actions(policy_engine):
    """Test checking multiple actions in batch."""
    actions = [
        {"action_type": "compile", "params": {}},
        {"action_type": "deploy", "params": {"environment": "staging"}},
        {"action_type": "query", "params": {"sql": "SELECT * FROM users"}}
    ]
    
    results = []
    for action in actions:
        result = await policy_engine.check_action(**action)
        results.append(result)
    
    assert len(results) == 3
    assert all(r["allowed"] for r in results)