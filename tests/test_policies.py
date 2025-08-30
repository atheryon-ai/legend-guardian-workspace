import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent import policies

def test_policies_has_expected_methods():
    assert hasattr(policies, "PolicyEngine")
    engine = policies.PolicyEngine()
    assert hasattr(engine, "_load_default_policies")
    assert hasattr(engine, "_load_policies_from_file")
    assert hasattr(engine, "check_action")
    assert hasattr(engine, "check_compile_result")
    assert hasattr(engine, "check_test_result")
