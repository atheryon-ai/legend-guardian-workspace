import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients import engine

def test_engine_has_expected_methods():
    assert hasattr(engine, "EngineClient")
    assert hasattr(engine.EngineClient, "__init__")
    assert hasattr(engine.EngineClient, "compile")
    assert hasattr(engine.EngineClient, "run_tests")
