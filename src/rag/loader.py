import os
import json
import yaml
from typing import List, Dict


class Loader:
    async def load_documents(self, paths: List[str]) -> List[Dict]:
        """Loads documents from a list of paths, supporting different file types."""
        documents = []
        for path in paths:
            try:
                file_extension = os.path.splitext(path)[1]
                with open(path, "r") as f:
                    if file_extension == ".json":
                        content = json.load(f)
                    elif file_extension in [".yaml", ".yml"]:
                        content = yaml.safe_load(f)
                    else:
                        content = f.read()
                documents.append({"path": path, "content": content})
            except Exception as e:
                print(f"Error loading document {path}: {e}")
        return documents


loader = Loader()
