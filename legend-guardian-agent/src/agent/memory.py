"""Memory store for agent episodic and action history."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class MemoryStore:
    """In-memory store for agent episodes and actions."""
    
    def __init__(self, max_episodes: int = 1000):
        """Initialize memory store."""
        self.max_episodes = max_episodes
        self.episodes = []
        self.actions = []
        self.context = {}
    
    def add_episode(self, episode: Dict[str, Any]) -> None:
        """
        Add an episode to memory.
        
        Args:
            episode: Episode data including prompt, plan, context
        """
        episode["timestamp"] = episode.get("timestamp", datetime.utcnow().isoformat())
        self.episodes.append(episode)
        
        # Maintain max size
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes:]
        
        logger.debug("Episode added to memory", episode_id=episode.get("id"))
    
    def add_action(self, action: Dict[str, Any]) -> None:
        """
        Add an action to memory.
        
        Args:
            action: Action data including type, params, result
        """
        action["timestamp"] = action.get("timestamp", datetime.utcnow().isoformat())
        self.actions.append(action)
        
        # Maintain reasonable size
        if len(self.actions) > self.max_episodes * 10:
            self.actions = self.actions[-(self.max_episodes * 10):]
        
        logger.debug("Action added to memory", action_type=action.get("action"))
    
    def get_recent_episodes(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent episodes.
        
        Args:
            count: Number of episodes to retrieve
        
        Returns:
            List of recent episodes
        """
        return self.episodes[-count:] if self.episodes else []
    
    def get_recent_actions(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent actions.
        
        Args:
            count: Number of actions to retrieve
        
        Returns:
            List of recent actions
        """
        return self.actions[-count:] if self.actions else []
    
    def find_similar_episodes(
        self,
        prompt: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Find similar episodes based on prompt.
        
        Args:
            prompt: Prompt to match
            limit: Maximum results
        
        Returns:
            List of similar episodes
        """
        # Simple keyword matching for demonstration
        # In production, use vector similarity
        prompt_lower = prompt.lower()
        keywords = set(prompt_lower.split())
        
        scored_episodes = []
        for episode in self.episodes:
            ep_prompt = episode.get("prompt", "").lower()
            ep_keywords = set(ep_prompt.split())
            
            # Calculate simple similarity score
            common = keywords.intersection(ep_keywords)
            score = len(common) / max(len(keywords), 1)
            
            if score > 0:
                scored_episodes.append((score, episode))
        
        # Sort by score and return top results
        scored_episodes.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored_episodes[:limit]]
    
    def get_context(self, key: str) -> Any:
        """
        Get context value.
        
        Args:
            key: Context key
        
        Returns:
            Context value or None
        """
        return self.context.get(key)
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set context value.
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def clear_context(self) -> None:
        """Clear all context."""
        self.context.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Statistics about memory usage
        """
        action_types = {}
        for action in self.actions:
            action_type = action.get("action", "unknown")
            action_types[action_type] = action_types.get(action_type, 0) + 1
        
        return {
            "episode_count": len(self.episodes),
            "action_count": len(self.actions),
            "context_keys": list(self.context.keys()),
            "action_types": action_types,
            "memory_usage_bytes": self._estimate_memory_usage(),
        }
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        try:
            episodes_json = json.dumps(self.episodes)
            actions_json = json.dumps(self.actions)
            context_json = json.dumps(self.context)
            return len(episodes_json) + len(actions_json) + len(context_json)
        except:
            return 0
    
    def export_history(self) -> Dict[str, Any]:
        """
        Export full history.
        
        Returns:
            Complete memory export
        """
        return {
            "episodes": self.episodes,
            "actions": self.actions,
            "context": self.context,
            "exported_at": datetime.utcnow().isoformat(),
        }
    
    def import_history(self, data: Dict[str, Any]) -> None:
        """
        Import history data.
        
        Args:
            data: History data to import
        """
        if "episodes" in data:
            self.episodes = data["episodes"]
        if "actions" in data:
            self.actions = data["actions"]
        if "context" in data:
            self.context = data["context"]
        
        logger.info("History imported", episode_count=len(self.episodes))