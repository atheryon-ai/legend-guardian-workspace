import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent import memory

def test_memory_has_expected_methods():
    assert hasattr(memory, "MemoryStore")
    store = memory.MemoryStore()
    assert hasattr(store, "add_episode")
    assert hasattr(store, "add_action")
    assert hasattr(store, "get_recent_episodes")
    assert hasattr(store, "get_recent_actions")
    assert hasattr(store, "get_context")
    assert hasattr(store, "get_statistics")
