"""Comprehensive tests for RAG Vector Store."""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
import math
import tempfile
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.rag.store import VectorStore


@pytest.fixture
def store():
    """Create a VectorStore instance."""
    return VectorStore()


@pytest.fixture
def store_with_persist():
    """Create a VectorStore with persistence."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp_path = tmp.name
    store = VectorStore(persist_path=tmp_path)
    yield store
    # Cleanup
    if Path(tmp_path).exists():
        Path(tmp_path).unlink()


def test_store_initialization(store):
    """Test VectorStore initialization."""
    assert store.documents == []
    assert store.vectors == []
    assert store.index is None
    assert store.persist_path is None


def test_store_initialization_with_persist_path():
    """Test VectorStore initialization with persist path."""
    store = VectorStore(persist_path="/tmp/test.json")
    assert store.persist_path == Path("/tmp/test.json")


def test_store_initialization_load_existing():
    """Test loading existing store on initialization."""
    test_data = {
        'documents': [{'content': 'test doc'}],
        'vectors': [[0.1, 0.2]]
    }
    
    with patch.object(Path, 'exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            store = VectorStore(persist_path="/tmp/existing.json")
            
    assert len(store.documents) == 1
    assert len(store.vectors) == 1


def test_add_documents(store):
    """Test adding documents to store."""
    docs = [
        {"content": "First document", "metadata": {"id": 1}},
        {"content": "Second document", "metadata": {"id": 2}}
    ]
    
    store.add_documents(docs)
    
    assert len(store.documents) == 2
    assert len(store.vectors) == 2
    assert store.documents[0]["content"] == "First document"


def test_add_documents_with_persist(store_with_persist):
    """Test adding documents with persistence."""
    docs = [{"content": "Test document"}]
    
    with patch.object(store_with_persist, 'save') as mock_save:
        store_with_persist.add_documents(docs)
        mock_save.assert_called_once()


def test_embed_text(store):
    """Test text embedding."""
    text = "Test text for embedding"
    embedding = store._embed_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 10
    assert all(isinstance(x, float) for x in embedding)
    assert all(0 <= x <= 1 for x in embedding)


def test_embed_text_empty(store):
    """Test embedding empty text."""
    embedding = store._embed_text("")
    
    assert embedding == [0.0] * 10


def test_embed_text_consistency(store):
    """Test that same text produces same embedding."""
    text = "Consistent text"
    embedding1 = store._embed_text(text)
    embedding2 = store._embed_text(text)
    
    assert embedding1 == embedding2


def test_search(store):
    """Test vector search."""
    # Add documents with embeddings
    store.documents = [
        {"content": "Python programming"},
        {"content": "Java development"},
        {"content": "Python tutorial"}
    ]
    store.vectors = [
        store._embed_text("Python programming"),
        store._embed_text("Java development"),
        store._embed_text("Python tutorial")
    ]
    
    results = store.search("Python", k=2)
    
    assert len(results) == 2
    assert all('similarity' in r for r in results)


def test_search_empty_store(store):
    """Test searching empty store."""
    results = store.search("query")
    assert results == []


def test_search_with_threshold(store):
    """Test search with similarity threshold."""
    store.documents = [
        {"content": "Exact match"},
        {"content": "Different content"}
    ]
    store.vectors = [
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    ]
    
    # Search with high threshold
    results = store.search("test", k=10, threshold=0.9)
    
    # Should return few or no results due to high threshold
    assert len(results) <= 1


def test_search_k_limit(store):
    """Test that search respects k limit."""
    # Add many documents
    for i in range(10):
        store.documents.append({"content": f"Document {i}"})
        store.vectors.append(store._embed_text(f"Document {i}"))
    
    results = store.search("Document", k=3)
    
    assert len(results) == 3


def test_cosine_similarity(store):
    """Test cosine similarity calculation."""
    # Test identical vectors
    sim1 = store._cosine_similarity([1, 0, 0], [1, 0, 0])
    assert sim1 == pytest.approx(1.0)
    
    # Test orthogonal vectors
    sim2 = store._cosine_similarity([1, 0, 0], [0, 1, 0])
    assert sim2 == pytest.approx(0.0)
    
    # Test opposite vectors
    sim3 = store._cosine_similarity([1, 0, 0], [-1, 0, 0])
    assert sim3 == pytest.approx(-1.0)


def test_cosine_similarity_empty_vectors(store):
    """Test cosine similarity with empty vectors."""
    sim = store._cosine_similarity([], [])
    assert sim == 0.0


def test_cosine_similarity_different_lengths(store):
    """Test cosine similarity with different length vectors."""
    sim = store._cosine_similarity([1, 0], [1, 0, 0])
    assert sim == 0.0


def test_cosine_similarity_zero_vectors(store):
    """Test cosine similarity with zero vectors."""
    sim = store._cosine_similarity([0, 0, 0], [1, 1, 1])
    assert sim == 0.0


def test_build_index(store):
    """Test building search index."""
    store.vectors = [[0.1, 0.2], [0.3, 0.4]]
    
    store.build_index()
    
    assert store.index is not None
    assert store.index is True


def test_clear(store):
    """Test clearing the store."""
    store.documents = [{"content": "test"}]
    store.vectors = [[0.1, 0.2]]
    store.index = True
    
    store.clear()
    
    assert store.documents == []
    assert store.vectors == []
    assert store.index is None


def test_clear_with_persist(store_with_persist):
    """Test clearing store with persistence."""
    store_with_persist.documents = [{"content": "test"}]
    store_with_persist.vectors = [[0.1]]
    
    # Create the file
    store_with_persist.save()
    assert store_with_persist.persist_path.exists()
    
    store_with_persist.clear()
    
    assert store_with_persist.documents == []
    assert store_with_persist.vectors == []
    assert not store_with_persist.persist_path.exists()


def test_save(store):
    """Test saving store to disk."""
    store.documents = [{"content": "test", "id": 1}]
    store.vectors = [[0.1, 0.2]]
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        store.save(tmp_path)
        
        with open(tmp_path, 'r') as f:
            data = json.load(f)
        
        assert data['documents'] == store.documents
        assert data['vectors'] == store.vectors
    finally:
        Path(tmp_path).unlink()


def test_save_default_path(store_with_persist):
    """Test saving with default persist path."""
    store_with_persist.documents = [{"content": "test"}]
    store_with_persist.vectors = [[0.1]]
    
    store_with_persist.save()
    
    assert store_with_persist.persist_path.exists()


def test_save_creates_directory(store):
    """Test that save creates parent directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "subdir" / "store.json"
        
        store.documents = [{"content": "test"}]
        store.vectors = [[0.1]]
        
        store.save(str(save_path))
        
        assert save_path.exists()


def test_load(store):
    """Test loading store from disk."""
    test_data = {
        'documents': [{"content": "loaded", "id": 1}],
        'vectors': [[0.3, 0.4]]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(test_data, tmp)
        tmp_path = tmp.name
    
    try:
        store.load(tmp_path)
        
        assert len(store.documents) == 1
        assert store.documents[0]["content"] == "loaded"
        assert store.vectors == [[0.3, 0.4]]
    finally:
        Path(tmp_path).unlink()


def test_load_nonexistent_file(store):
    """Test loading from non-existent file."""
    store.load("/nonexistent/file.json")
    
    # Should remain empty
    assert store.documents == []
    assert store.vectors == []


def test_load_default_path(store_with_persist):
    """Test loading with default persist path."""
    test_data = {
        'documents': [{"content": "test"}],
        'vectors': [[0.5]]
    }
    
    with open(store_with_persist.persist_path, 'w') as f:
        json.dump(test_data, f)
    
    store_with_persist.load()
    
    assert len(store_with_persist.documents) == 1


def test_get_statistics(store):
    """Test getting store statistics."""
    store.documents = [
        {"content": "doc1"},
        {"content": "doc2"},
        {"content": "doc3"}
    ]
    store.vectors = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    store.index = True
    
    stats = store.get_statistics()
    
    assert stats['document_count'] == 3
    assert stats['vector_dimensions'] == 2
    assert stats['index_built'] is True
    assert 'memory_usage' in stats
    assert stats['memory_usage'] > 0


def test_get_statistics_empty(store):
    """Test statistics for empty store."""
    stats = store.get_statistics()
    
    assert stats['document_count'] == 0
    assert stats['vector_dimensions'] == 0
    assert stats['index_built'] is False
    assert stats['memory_usage'] == 0


@pytest.mark.asyncio
async def test_query(store):
    """Test async query method."""
    # Documents should be a list, not a dict
    store.documents = [
        {"content": "Python programming guide", "id": "1"},
        {"content": "Java development tutorial", "id": "2"},
        {"content": "Python data science", "id": "3"}
    ]
    
    results = await store.query("python", top_k=2)
    
    assert len(results) <= 2


@pytest.mark.asyncio
async def test_query_with_filters(store):
    """Test query with filters."""
    store.documents = [
        {"content": "Test doc 1", "category": "A", "id": "1"},
        {"content": "Test doc 2", "category": "B", "id": "2"},
        {"content": "Test doc 3", "category": "A", "id": "3"}
    ]
    
    results = await store.query(
        "test",
        top_k=5,
        filters={"category": "A"}
    )
    
    # Should only return documents with category A
    for doc in results:
        assert doc.get("category") == "A"


@pytest.mark.asyncio
async def test_query_empty_store(store):
    """Test querying empty store."""
    results = await store.query("test")
    assert results == []


@pytest.mark.asyncio
async def test_delete_documents(store):
    """Test deleting documents."""
    store.documents = [
        {"content": "doc1", "id": "1"},
        {"content": "doc2", "id": "2"},
        {"content": "doc3", "id": "3"}
    ]
    store.vectors = [[0.1], [0.2], [0.3]]  # Add corresponding vectors
    
    await store.delete_documents(["1", "3"])
    
    assert len(store.documents) == 1
    assert len(store.vectors) == 1
    # Check that doc with id "2" remains
    remaining_ids = [doc.get("id") for doc in store.documents]
    assert "2" in remaining_ids
    assert "1" not in remaining_ids
    assert "3" not in remaining_ids


@pytest.mark.asyncio
async def test_delete_documents_with_persist(store_with_persist):
    """Test deleting documents with persistence."""
    store_with_persist.documents = [
        {"content": "doc1", "id": "1"}
    ]
    store_with_persist.vectors = [[0.1]]
    
    with patch.object(store_with_persist, 'save') as mock_save:
        await store_with_persist.delete_documents(["1"])
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_delete_nonexistent_documents(store):
    """Test deleting non-existent documents."""
    store.documents = [{"content": "doc1", "id": "1"}]
    store.vectors = [[0.1]]
    
    # Should not raise error
    await store.delete_documents(["2", "3"])
    
    assert len(store.documents) == 1


def test_search_similarity_ordering(store):
    """Test that search results are ordered by similarity."""
    store.documents = [
        {"content": "A"},
        {"content": "B"},
        {"content": "C"}
    ]
    # Create vectors with decreasing similarity to query
    store.vectors = [
        [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    ]
    
    with patch.object(store, '_embed_text') as mock_embed:
        # Query vector similar to first document
        mock_embed.return_value = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
        
        results = store.search("query", k=3)
        
        # First result should have highest similarity
        if len(results) > 1:
            assert results[0]['similarity'] >= results[1]['similarity']


def test_add_documents_creates_embeddings(store):
    """Test that add_documents creates embeddings."""
    docs = [
        {"content": "Document 1"},
        {"content": "Document 2"}
    ]
    
    store.add_documents(docs)
    
    assert len(store.vectors) == 2
    assert all(len(vec) == 10 for vec in store.vectors)


def test_memory_usage_calculation(store):
    """Test memory usage calculation in statistics."""
    # Add some large documents
    for i in range(100):
        store.documents.append({"content": "x" * 1000})
        store.vectors.append([0.1] * 10)
    
    stats = store.get_statistics()
    
    # Memory usage should be substantial
    assert stats['memory_usage'] > 1000