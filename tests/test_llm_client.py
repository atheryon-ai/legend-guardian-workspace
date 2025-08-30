import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent import llm_client

def test_llm_client_has_expected_methods():
    assert hasattr(llm_client, "LLMClient")
    client = llm_client.LLMClient()
    assert hasattr(client, "parse_intent")
    assert hasattr(client, "generate_response")
    assert hasattr(client, "analyze_error")
