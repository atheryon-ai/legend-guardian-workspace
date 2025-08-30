import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian import config

def test_config_has_expected_attributes():
    s = config.settings
    assert hasattr(s, "app_name")
    assert hasattr(s, "app_version")
    assert hasattr(s, "engine_url")
    assert hasattr(s, "rag_enabled")
    assert hasattr(s, "max_request_size")
