import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent import orchestrator

def test_orchestrator_has_expected_methods():
    assert hasattr(orchestrator, "AgentOrchestrator")
    # Only check for class and some method names
    assert hasattr(orchestrator.AgentOrchestrator, "__init__")
    assert hasattr(orchestrator.AgentOrchestrator, "parse_intent")
    assert hasattr(orchestrator.AgentOrchestrator, "execute_step")
    assert hasattr(orchestrator.AgentOrchestrator, "validate_step")
