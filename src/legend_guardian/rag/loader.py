"""Document loader for RAG system."""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


class Loader:
    """Loads and processes documents for the RAG system."""
    
    def __init__(self):
        """Initialize the document loader."""
        self.supported_extensions = {'.txt', '.md', '.json', '.yaml', '.yml'}
    
    async def load_documents(self, paths: List[str]) -> List[Dict[str, Any]]:
        """
        Load documents from specified paths.
        
        Args:
            paths: List of file paths to load
            
        Returns:
            List of loaded documents with metadata
        """
        documents = []
        
        for path_str in paths:
            path = Path(path_str)
            
            if not path.exists():
                continue
                
            if path.is_file():
                doc = await self._load_file(path)
                if doc:
                    documents.append(doc)
            elif path.is_dir():
                for file_path in path.rglob('*'):
                    if file_path.suffix in self.supported_extensions:
                        doc = await self._load_file(file_path)
                        if doc:
                            documents.append(doc)
        
        return documents
    
    async def _load_file(self, path: Path) -> Dict[str, Any]:
        """
        Load a single file.
        
        Args:
            path: File path
            
        Returns:
            Document dict with content and metadata
        """
        try:
            if path.suffix in {'.json'}:
                with open(path, 'r') as f:
                    content = json.load(f)
            elif path.suffix in {'.yaml', '.yml'}:
                with open(path, 'r') as f:
                    content = yaml.safe_load(f)
            else:
                with open(path, 'r') as f:
                    content = f.read()
            
            return {
                'path': str(path),
                'name': path.name,
                'content': content,
                'type': path.suffix[1:] if path.suffix else 'unknown'
            }
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None