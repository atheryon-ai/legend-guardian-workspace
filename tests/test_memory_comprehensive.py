"""Comprehensive tests for Memory Store."""

import pytest
from datetime import datetime
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.agent.memory import MemoryStore


@pytest.fixture
def memory_store():
    """Create a memory store instance."""
    return MemoryStore()


def test_memory_store_initialization():
    """Test MemoryStore initialization."""
    store = MemoryStore()
    assert store.episodes == []
    assert store.actions == []
    assert store.context == {}


def test_add_episode(memory_store):
    """Test adding an episode."""
    episode = {
        "id": "ep1",
        "prompt": "Create a new model",
        "plan": {"steps": ["step1", "step2"]}
    }
    memory_store.add_episode(episode)
    
    assert len(memory_store.episodes) == 1
    saved_episode = memory_store.episodes[0]
    assert saved_episode["id"] == "ep1"
    assert saved_episode["prompt"] == "Create a new model"
    assert saved_episode["plan"] == {"steps": ["step1", "step2"]}
    assert "timestamp" in saved_episode


def test_add_episode_with_metadata(memory_store):
    """Test adding an episode with metadata."""
    episode = {
        "id": "ep2",
        "prompt": "Deploy service",
        "plan": {"action": "deploy"},
        "metadata": {"user": "test_user", "project": "test_project"}
    }
    memory_store.add_episode(episode)
    
    saved_episode = memory_store.episodes[0]
    assert saved_episode["metadata"] == {"user": "test_user", "project": "test_project"}


def test_add_action(memory_store):
    """Test adding an action."""
    action = {
        "id": "act1",
        "action": "compile",
        "params": {"model": "test_model"},
        "result": {"status": "success"}
    }
    memory_store.add_action(action)
    
    assert len(memory_store.actions) == 1
    saved_action = memory_store.actions[0]
    assert saved_action["id"] == "act1"
    assert saved_action["action"] == "compile"
    assert saved_action["params"] == {"model": "test_model"}
    assert saved_action["result"] == {"status": "success"}
    assert "timestamp" in saved_action


def test_get_recent_episodes(memory_store):
    """Test getting recent episodes."""
    # Add multiple episodes
    for i in range(5):
        episode = {
            "id": f"ep{i}",
            "prompt": f"Intent {i}",
            "plan": {"step": i}
        }
        memory_store.add_episode(episode)
    
    # Get recent 3
    recent = memory_store.get_recent_episodes(count=3)
    assert len(recent) == 3
    
    # Should return last 3 episodes
    assert recent[0]["prompt"] == "Intent 2"
    assert recent[1]["prompt"] == "Intent 3"
    assert recent[2]["prompt"] == "Intent 4"


def test_get_recent_episodes_all(memory_store):
    """Test getting all episodes when count > total."""
    for i in range(3):
        episode = {"id": f"ep{i}", "prompt": f"Intent {i}", "plan": {}}
        memory_store.add_episode(episode)
    
    recent = memory_store.get_recent_episodes(count=10)
    assert len(recent) == 3


def test_get_recent_actions(memory_store):
    """Test getting recent actions."""
    # Add multiple actions
    for i in range(5):
        action = {
            "id": f"act{i}",
            "action": f"action_{i}",
            "params": {},
            "result": {"index": i}
        }
        memory_store.add_action(action)
    
    # Get recent 3
    recent = memory_store.get_recent_actions(count=3)
    assert len(recent) == 3
    
    # Should return last 3 actions
    assert recent[0]["action"] == "action_2"
    assert recent[1]["action"] == "action_3"
    assert recent[2]["action"] == "action_4"


# update_episode_status method doesn't exist in actual implementation


def test_set_context(memory_store):
    """Test setting context values."""
    memory_store.set_context("project_id", "proj123")
    memory_store.set_context("user", {"id": "user1", "name": "Test User"})
    
    assert memory_store.context["project_id"] == "proj123"
    assert memory_store.context["user"]["id"] == "user1"


def test_get_context(memory_store):
    """Test getting context values."""
    memory_store.set_context("key1", "value1")
    
    assert memory_store.get_context("key1") == "value1"
    assert memory_store.get_context("nonexistent") is None




# get_episode_actions method doesn't exist in actual implementation


def test_get_statistics(memory_store):
    """Test getting memory statistics."""
    # Add some data
    memory_store.add_episode({"id": "ep1", "prompt": "Test 1", "plan": {}})
    memory_store.add_episode({"id": "ep2", "prompt": "Test 2", "plan": {}})
    
    memory_store.add_action({"action": "compile", "result": {"status": "success"}})
    memory_store.add_action({"action": "test", "result": {"status": "failure"}})
    memory_store.add_action({"action": "deploy", "result": {"status": "success"}})
    
    stats = memory_store.get_statistics()
    
    assert stats["episode_count"] == 2
    assert stats["action_count"] == 3
    assert "compile" in stats["action_types"]
    assert stats["action_types"]["compile"] == 1
    assert stats["action_types"]["test"] == 1
    assert stats["action_types"]["deploy"] == 1
    assert "memory_usage_bytes" in stats


def test_get_statistics_empty(memory_store):
    """Test statistics for empty store."""
    stats = memory_store.get_statistics()
    
    assert stats["episode_count"] == 0
    assert stats["action_count"] == 0
    assert stats["action_types"] == {}
    assert stats["context_keys"] == []


def test_clear_context(memory_store):
    """Test clearing context."""
    # Add data
    memory_store.set_context("key1", "value1")
    memory_store.set_context("key2", "value2")
    
    # Clear context
    memory_store.clear_context()
    
    assert memory_store.context == {}
    assert memory_store.get_context("key1") is None


def test_export_history(memory_store):
    """Test exporting history."""
    # Add data
    memory_store.add_episode({
        "id": "ep1",
        "prompt": "Test export",
        "plan": {"steps": ["s1", "s2"]},
        "metadata": {"user": "test"}
    })
    memory_store.add_action({
        "action": "compile",
        "params": {"model": "m1"},
        "result": {"status": "ok"}
    })
    memory_store.set_context("project", "proj1")
    
    # Export
    export = memory_store.export_history()
    
    assert "episodes" in export
    assert "actions" in export
    assert "context" in export
    assert "exported_at" in export
    assert len(export["episodes"]) == 1
    assert len(export["actions"]) == 1
    assert export["context"]["project"] == "proj1"
    
    # Check episode data
    ep = export["episodes"][0]
    assert ep["prompt"] == "Test export"
    assert ep["plan"] == {"steps": ["s1", "s2"]}
    assert ep["metadata"] == {"user": "test"}
    
    # Check action data
    action = export["actions"][0]
    assert action["action"] == "compile"
    assert action["params"] == {"model": "m1"}
    assert action["result"] == {"status": "ok"}


def test_import_history(memory_store):
    """Test importing history."""
    import_data = {
        "episodes": [
            {
                "id": "ep1",
                "prompt": "Imported intent",
                "plan": {"imported": True},
                "metadata": {"source": "import"}
            }
        ],
        "actions": [
            {
                "id": "act1",
                "action": "imported_action",
                "params": {"param1": "value1"},
                "result": {"imported": True}
            }
        ],
        "context": {
            "imported_key": "imported_value"
        }
    }
    
    memory_store.import_history(import_data)
    
    assert len(memory_store.episodes) == 1
    assert len(memory_store.actions) == 1
    assert memory_store.context["imported_key"] == "imported_value"
    
    episode = memory_store.episodes[0]
    assert episode["prompt"] == "Imported intent"
    assert episode["metadata"]["source"] == "import"
    
    action = memory_store.actions[0]
    assert action["action"] == "imported_action"
    assert action["params"]["param1"] == "value1"


def test_find_similar_episodes(memory_store):
    """Test finding similar episodes."""
    memory_store.add_episode({"prompt": "Create model Person", "plan": {}})
    memory_store.add_episode({"prompt": "Deploy service", "plan": {}})
    memory_store.add_episode({"prompt": "Create model Company", "plan": {}})
    
    # Search for "model"
    results = memory_store.find_similar_episodes("model creation", limit=2)
    assert len(results) <= 2
    # Similar episodes should have "model" in them
    for result in results:
        assert "model" in result["prompt"].lower() or "create" in result["prompt"].lower()


# Episode and Action classes don't exist in the actual implementation