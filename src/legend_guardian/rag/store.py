"""Vector store for RAG system."""

from typing import Dict, List, Any, Optional
import json
from pathlib import Path


class VectorStore:
    """Simple in-memory vector store for RAG system."""
    
    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            persist_path: Optional path to persist the store
        """
        self.documents = {}
        self.persist_path = Path(persist_path) if persist_path else None
        
        if self.persist_path and self.persist_path.exists():
            self.load()
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the store.
        
        Args:
            documents: List of documents to add
        """
        for doc in documents:
            doc_id = doc.get('path', str(len(self.documents)))
            self.documents[doc_id] = doc
        
        if self.persist_path:
            self.save()
    
    async def query(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector store.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            filters: Optional filters to apply
            
        Returns:
            List of relevant documents
        """
        # Simple keyword-based search for now
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self.documents.items():
            content = str(doc.get('content', '')).lower()
            
            # Apply filters if provided
            if filters:
                match = True
                for key, value in filters.items():
                    if doc.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Simple relevance scoring based on keyword occurrence
            score = content.count(query_lower)
            if score > 0:
                results.append({
                    'document': doc,
                    'score': score
                })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return [r['document'] for r in results[:top_k]]
    
    async def delete_documents(self, doc_ids: List[str]) -> None:
        """
        Delete documents from the store.
        
        Args:
            doc_ids: List of document IDs to delete
        """
        for doc_id in doc_ids:
            self.documents.pop(doc_id, None)
        
        if self.persist_path:
            self.save()
    
    def save(self) -> None:
        """Save the store to disk."""
        if self.persist_path:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, 'w') as f:
                json.dump(self.documents, f, indent=2)
    
    def load(self) -> None:
        """Load the store from disk."""
        if self.persist_path and self.persist_path.exists():
            with open(self.persist_path, 'r') as f:
                self.documents = json.load(f)
    
    def clear(self) -> None:
        """Clear all documents from the store."""
        self.documents.clear()
        if self.persist_path and self.persist_path.exists():
            self.persist_path.unlink()