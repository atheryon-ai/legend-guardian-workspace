"""Document loader for RAG system."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import yaml

logger = structlog.get_logger()


class DocumentLoader:
    """Load and process documents for RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document loader.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = []
    
    def load_pure_examples(self, directory: str) -> List[Dict[str, Any]]:
        """
        Load PURE code examples from directory.
        
        Args:
            directory: Directory containing PURE files
        
        Returns:
            List of document chunks
        """
        documents = []
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Directory not found: {directory}")
            return documents
        
        for file_path in path.glob("**/*.pure"):
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    
                # Extract metadata from PURE code
                metadata = self._extract_pure_metadata(content)
                
                # Chunk the content
                chunks = self._chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "content": chunk,
                        "metadata": {
                            **metadata,
                            "source": str(file_path),
                            "chunk_id": i,
                            "type": "pure_code"
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} PURE document chunks")
        return documents
    
    def load_legend_docs(self, directory: str) -> List[Dict[str, Any]]:
        """
        Load Legend documentation.
        
        Args:
            directory: Directory containing docs
        
        Returns:
            List of document chunks
        """
        documents = []
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Directory not found: {directory}")
            return documents
        
        # Load Markdown files
        for file_path in path.glob("**/*.md"):
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Extract sections
                sections = self._extract_markdown_sections(content)
                
                for section in sections:
                    chunks = self._chunk_text(section["content"])
                    
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "content": chunk,
                            "metadata": {
                                "source": str(file_path),
                                "section": section["title"],
                                "chunk_id": i,
                                "type": "documentation"
                            }
                        })
                        
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} documentation chunks")
        return documents
    
    def load_mapping_examples(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load mapping examples from JSON/YAML file.
        
        Args:
            file_path: Path to mapping examples file
        
        Returns:
            List of mapping examples
        """
        documents = []
        
        try:
            with open(file_path, "r") as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            mappings = data.get("mappings", [])
            
            for mapping in mappings:
                documents.append({
                    "content": json.dumps(mapping, indent=2),
                    "metadata": {
                        "source": file_path,
                        "mapping_type": mapping.get("type", "unknown"),
                        "model": mapping.get("model"),
                        "type": "mapping_example"
                    }
                })
                
        except Exception as e:
            logger.error(f"Failed to load mappings from {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} mapping examples")
        return documents
    
    def load_policies(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load policy documents.
        
        Args:
            file_path: Path to policy file
        
        Returns:
            List of policy documents
        """
        documents = []
        
        try:
            with open(file_path, "r") as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Process different policy types
            for policy_type, policies in data.items():
                if isinstance(policies, list):
                    for policy in policies:
                        documents.append({
                            "content": json.dumps(policy, indent=2),
                            "metadata": {
                                "source": file_path,
                                "policy_type": policy_type,
                                "type": "policy"
                            }
                        })
                elif isinstance(policies, dict):
                    documents.append({
                        "content": json.dumps(policies, indent=2),
                        "metadata": {
                            "source": file_path,
                            "policy_type": policy_type,
                            "type": "policy"
                        }
                    })
                    
        except Exception as e:
            logger.error(f"Failed to load policies from {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} policy documents")
        return documents
    
    def load_api_specs(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load API specifications (OpenAPI/Swagger).
        
        Args:
            file_path: Path to API spec file
        
        Returns:
            List of API spec documents
        """
        documents = []
        
        try:
            with open(file_path, "r") as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
            
            # Extract paths and operations
            paths = spec.get("paths", {})
            
            for path, operations in paths.items():
                for method, operation in operations.items():
                    if isinstance(operation, dict):
                        documents.append({
                            "content": json.dumps({
                                "path": path,
                                "method": method,
                                "operation": operation
                            }, indent=2),
                            "metadata": {
                                "source": file_path,
                                "api_path": path,
                                "http_method": method,
                                "operation_id": operation.get("operationId"),
                                "type": "api_spec"
                            }
                        })
                        
        except Exception as e:
            logger.error(f"Failed to load API spec from {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} API spec documents")
        return documents
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        chunks = []
        
        if len(text) <= self.chunk_size:
            return [text]
        
        # Simple chunking by character count with overlap
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at a natural boundary (newline, period, space)
            if end < len(text):
                for separator in ["\n\n", "\n", ". ", " "]:
                    last_sep = text.rfind(separator, start, end)
                    if last_sep > start:
                        end = last_sep + len(separator)
                        break
            
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
            
            # Avoid infinite loop
            if start >= len(text) - 1:
                break
        
        return chunks
    
    def _extract_pure_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from PURE code.
        
        Args:
            content: PURE code content
        
        Returns:
            Metadata dictionary
        """
        metadata = {}
        
        # Extract class names
        import re
        class_pattern = r"Class\s+(\S+)"
        classes = re.findall(class_pattern, content)
        if classes:
            metadata["classes"] = classes
        
        # Extract function names
        func_pattern = r"function\s+(\w+)"
        functions = re.findall(func_pattern, content)
        if functions:
            metadata["functions"] = functions
        
        # Extract mapping names
        mapping_pattern = r"Mapping\s+(\S+)"
        mappings = re.findall(mapping_pattern, content)
        if mappings:
            metadata["mappings"] = mappings
        
        return metadata
    
    def _extract_markdown_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Extract sections from Markdown content.
        
        Args:
            content: Markdown content
        
        Returns:
            List of sections with titles and content
        """
        sections = []
        lines = content.split("\n")
        
        current_section = {"title": "Introduction", "content": ""}
        
        for line in lines:
            if line.startswith("#"):
                # New section
                if current_section["content"]:
                    sections.append(current_section)
                
                # Extract title without # symbols
                title = line.lstrip("#").strip()
                current_section = {"title": title, "content": ""}
            else:
                current_section["content"] += line + "\n"
        
        # Add last section
        if current_section["content"]:
            sections.append(current_section)
        
        return sections