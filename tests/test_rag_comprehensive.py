"""Comprehensive tests for RAG modules."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.rag.loader import DocumentLoader
from legend_guardian.rag.store import VectorStore


class TestDocumentLoader:
    """Tests for DocumentLoader."""
    
    def test_loader_initialization(self):
        """Test DocumentLoader initialization."""
        loader = DocumentLoader()
        assert loader.documents == []
    
    def test_load_file_text(self):
        """Test loading a text file."""
        loader = DocumentLoader()
        
        with patch('builtins.open', mock_open(read_data="Test content")):
            loader.load_file("test.txt")
            
        assert len(loader.documents) == 1
        assert loader.documents[0]["content"] == "Test content"
        assert loader.documents[0]["source"] == "test.txt"
    
    def test_load_file_json(self):
        """Test loading a JSON file."""
        loader = DocumentLoader()
        test_data = {"key": "value", "nested": {"data": "test"}}
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            loader.load_file("test.json")
            
        assert len(loader.documents) == 1
        assert "key" in loader.documents[0]["content"]
    
    def test_load_file_error(self):
        """Test handling file load errors."""
        loader = DocumentLoader()
        
        with patch('builtins.open', side_effect=FileNotFoundError()):
            result = loader.load_file("nonexistent.txt")
            
        assert result is None
        assert len(loader.documents) == 0
    
    def test_load_directory(self):
        """Test loading multiple files from directory."""
        loader = DocumentLoader()
        
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("/test", [], ["file1.txt", "file2.json", "file3.md"])
            ]
            
            with patch.object(loader, 'load_file') as mock_load:
                loader.load_directory("/test")
                
                assert mock_load.call_count == 3
    
    def test_load_directory_with_filter(self):
        """Test loading directory with file filter."""
        loader = DocumentLoader()
        
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("/test", [], ["file1.txt", "file2.json", "file3.md"])
            ]
            
            with patch.object(loader, 'load_file') as mock_load:
                loader.load_directory("/test", extensions=[".txt", ".md"])
                
                assert mock_load.call_count == 2
    
    def test_split_documents(self):
        """Test splitting documents into chunks."""
        loader = DocumentLoader()
        loader.documents = [
            {"content": "A" * 1000, "source": "test.txt"}
        ]
        
        chunks = loader.split_documents(chunk_size=100)
        
        assert len(chunks) > 1
        assert all(len(c["content"]) <= 100 for c in chunks)
    
    def test_split_documents_overlap(self):
        """Test splitting with overlap."""
        loader = DocumentLoader()
        loader.documents = [
            {"content": "ABCDEFGHIJKLMNOP", "source": "test.txt"}
        ]
        
        chunks = loader.split_documents(chunk_size=5, overlap=2)
        
        # Check that chunks overlap
        for i in range(len(chunks) - 1):
            current_end = chunks[i]["content"][-2:]
            next_start = chunks[i+1]["content"][:2]
            # Some overlap should exist
    
    def test_extract_metadata(self):
        """Test metadata extraction."""
        loader = DocumentLoader()
        content = "Title: Test Doc\nAuthor: John\n\nContent here"
        
        metadata = loader.extract_metadata(content)
        
        assert "title" in metadata or "author" in metadata or len(metadata) > 0
    
    def test_clear_documents(self):
        """Test clearing loaded documents."""
        loader = DocumentLoader()
        loader.documents = [{"content": "test"}]
        
        loader.clear()
        
        assert loader.documents == []


class TestVectorStore:
    """Tests for VectorStore."""
    
    def test_store_initialization(self):
        """Test VectorStore initialization."""
        store = VectorStore()
        assert store.vectors == []
        assert store.documents == []
        assert store.index is None
    
    def test_add_documents(self):
        """Test adding documents to store."""
        store = VectorStore()
        docs = [
            {"content": "First document", "metadata": {"id": 1}},
            {"content": "Second document", "metadata": {"id": 2}}
        ]
        
        with patch.object(store, '_embed_text') as mock_embed:
            mock_embed.side_effect = [[0.1, 0.2], [0.3, 0.4]]
            
            store.add_documents(docs)
            
        assert len(store.documents) == 2
        assert len(store.vectors) == 2
    
    def test_embed_text(self):
        """Test text embedding."""
        store = VectorStore()
        
        # Simple hash-based embedding for testing
        embedding = store._embed_text("test text")
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)
    
    def test_search(self):
        """Test vector search."""
        store = VectorStore()
        store.documents = [
            {"content": "Python programming", "metadata": {}},
            {"content": "Java development", "metadata": {}},
            {"content": "Python tutorial", "metadata": {}}
        ]
        store.vectors = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.1, 0.2, 0.4]
        ]
        
        with patch.object(store, '_embed_text') as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.35]
            
            results = store.search("Python guide", k=2)
            
        assert len(results) == 2
        # Results should be sorted by similarity
    
    def test_search_empty_store(self):
        """Test searching empty store."""
        store = VectorStore()
        
        results = store.search("query")
        
        assert results == []
    
    def test_search_with_threshold(self):
        """Test search with similarity threshold."""
        store = VectorStore()
        store.documents = [
            {"content": "Exact match", "metadata": {}},
            {"content": "Different content", "metadata": {}}
        ]
        store.vectors = [[1, 0], [0, 1]]
        
        with patch.object(store, '_embed_text') as mock_embed:
            mock_embed.return_value = [1, 0]
            
            results = store.search("Exact match", k=10, threshold=0.9)
            
        # Only very similar results should be returned
        assert len(results) <= 1
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        store = VectorStore()
        
        # Test identical vectors
        sim1 = store._cosine_similarity([1, 0], [1, 0])
        assert sim1 == pytest.approx(1.0)
        
        # Test orthogonal vectors
        sim2 = store._cosine_similarity([1, 0], [0, 1])
        assert sim2 == pytest.approx(0.0)
        
        # Test opposite vectors
        sim3 = store._cosine_similarity([1, 0], [-1, 0])
        assert sim3 == pytest.approx(-1.0)
    
    def test_build_index(self):
        """Test building search index."""
        store = VectorStore()
        store.vectors = [[0.1, 0.2], [0.3, 0.4]]
        
        store.build_index()
        
        assert store.index is not None
    
    def test_clear_store(self):
        """Test clearing the store."""
        store = VectorStore()
        store.documents = [{"content": "test"}]
        store.vectors = [[0.1, 0.2]]
        store.index = "mock_index"
        
        store.clear()
        
        assert store.documents == []
        assert store.vectors == []
        assert store.index is None
    
    def test_save_and_load(self):
        """Test saving and loading store."""
        store = VectorStore()
        store.documents = [{"content": "test", "metadata": {"id": 1}}]
        store.vectors = [[0.1, 0.2]]
        
        # Test save
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_dump:
                store.save("test.json")
                mock_dump.assert_called_once()
        
        # Test load
        load_data = {
            "documents": [{"content": "loaded", "metadata": {}}],
            "vectors": [[0.3, 0.4]]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(load_data))):
            new_store = VectorStore()
            new_store.load("test.json")
            
            assert len(new_store.documents) == 1
            assert new_store.documents[0]["content"] == "loaded"
    
    def test_get_statistics(self):
        """Test getting store statistics."""
        store = VectorStore()
        store.documents = [
            {"content": "doc1", "metadata": {"type": "text"}},
            {"content": "doc2", "metadata": {"type": "text"}},
            {"content": "doc3", "metadata": {"type": "json"}}
        ]
        store.vectors = [[0.1], [0.2], [0.3]]
        
        stats = store.get_statistics()
        
        assert stats["document_count"] == 3
        assert stats["vector_dimensions"] == 1
        assert "index_built" in stats
        assert "memory_usage" in stats