
import datetime
import json
from typing import Dict, Any


class Memory:
    def __init__(self, episode_dir: str = "episodes"):
        self.episode_dir = episode_dir

    async def save_episode(self, intent: str, plan: Dict[str, Any], results: Dict[str, Any]):
        """Saves a record of an interaction to a JSON file."""
        timestamp = datetime.datetime.utcnow().isoformat()
        episode = {
            "intent": intent,
            "plan": plan,
            "results": results,
            "timestamp": timestamp
        }
        
        filename = f"{self.episode_dir}/{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(episode, f, indent=4)


memory = Memory()
