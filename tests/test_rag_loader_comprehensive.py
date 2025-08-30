"""Comprehensive tests for RAG Loader."""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
import yaml
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.rag.loader import Loader


@pytest.fixture
def loader():
    """Create a Loader instance."""
    return Loader()


def test_loader_initialization(loader):
    """Test Loader initialization."""
    assert loader.supported_extensions == {'.txt', '.md', '.json', '.yaml', '.yml'}
    assert loader.documents == []


def test_load_file_text(loader):
    """Test loading a text file."""
    test_content = "This is test content"
    
    with patch('builtins.open', mock_open(read_data=test_content)):
        result = loader.load_file("test.txt")
        
    assert result is not None
    assert result['content'] == test_content
    assert result['source'] == "test.txt"
    assert len(loader.documents) == 1


def test_load_file_json(loader):
    """Test loading a JSON file."""
    test_data = {"key": "value", "number": 42}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        result = loader.load_file("test.json")
        
    assert result is not None
    # JSON files are stored as strings in the loader
    assert json.loads(result['content']) == test_data
    assert result['source'] == "test.json"


def test_load_file_nonexistent(loader):
    """Test loading a non-existent file."""
    with patch('builtins.open', side_effect=FileNotFoundError()):
        result = loader.load_file("nonexistent.txt")
        
    assert result is None
    assert len(loader.documents) == 0


def test_load_file_with_error(loader):
    """Test loading file with read error."""
    with patch('builtins.open', side_effect=PermissionError("Access denied")):
        result = loader.load_file("forbidden.txt")
        
    assert result is None


def test_load_directory(loader):
    """Test loading all files from a directory."""
    mock_files = ["file1.txt", "file2.json", "file3.md", "file4.py"]
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ("/test/dir", [], mock_files)
        ]
        
        with patch.object(loader, 'load_file') as mock_load:
            mock_load.return_value = {"content": "test", "source": "test"}
            
            loader.load_directory("/test/dir")
            
            # Should only load supported extensions
            assert mock_load.call_count == 3  # .txt, .json, .md


def test_load_directory_with_extensions_filter(loader):
    """Test loading directory with specific extensions."""
    mock_files = ["file1.txt", "file2.json", "file3.md"]
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ("/test/dir", [], mock_files)
        ]
        
        with patch.object(loader, 'load_file') as mock_load:
            mock_load.return_value = {"content": "test", "source": "test"}
            
            loader.load_directory("/test/dir", extensions=[".txt", ".md"])
            
            assert mock_load.call_count == 2  # Only .txt and .md


def test_load_directory_recursive(loader):
    """Test loading directory recursively."""
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ("/test", ["subdir"], ["file1.txt"]),
            ("/test/subdir", [], ["file2.md"])
        ]
        
        with patch.object(loader, 'load_file') as mock_load:
            mock_load.return_value = {"content": "test", "source": "test"}
            
            loader.load_directory("/test")
            
            assert mock_load.call_count == 2


def test_split_documents(loader):
    """Test splitting documents into chunks."""
    # Add some documents
    loader.documents = [
        {"content": "A" * 1000, "source": "doc1.txt"},
        {"content": "B" * 500, "source": "doc2.txt"}
    ]
    
    chunks = loader.split_documents(chunk_size=100)
    
    # First document should be split into 10 chunks
    # Second document should be split into 5 chunks
    assert len(chunks) == 15
    assert all(len(chunk['content']) <= 100 for chunk in chunks)


def test_split_documents_with_overlap(loader):
    """Test splitting documents with overlap."""
    loader.documents = [
        {"content": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "source": "test.txt"}
    ]
    
    chunks = loader.split_documents(chunk_size=10, overlap=3)
    
    # Check overlapping
    for i in range(len(chunks) - 1):
        if i > 0:  # Skip first chunk
            current_end = chunks[i]['content'][-3:]
            next_start = chunks[i+1]['content'][:3]
            # The overlap means characters should repeat


def test_split_documents_empty(loader):
    """Test splitting with no documents."""
    chunks = loader.split_documents()
    assert chunks == []


def test_extract_metadata(loader):
    """Test extracting metadata from content."""
    content = """Title: Test Document
Author: John Doe
Date: 2024-01-01
Category: Testing

This is the actual content."""
    
    metadata = loader.extract_metadata(content)
    
    assert metadata['title'] == "Test Document"
    assert metadata['author'] == "John Doe"
    assert metadata['date'] == "2024-01-01"
    assert metadata['category'] == "Testing"


def test_extract_metadata_no_metadata(loader):
    """Test extracting metadata when none exists."""
    content = "Just plain content with no metadata"
    
    metadata = loader.extract_metadata(content)
    
    assert metadata == {}


def test_extract_metadata_partial(loader):
    """Test extracting partial metadata."""
    content = """Title: Test
Some content without more metadata"""
    
    metadata = loader.extract_metadata(content)
    
    assert metadata['title'] == "Test"
    assert len(metadata) == 1


def test_clear_documents(loader):
    """Test clearing documents."""
    loader.documents = [{"content": "test1"}, {"content": "test2"}]
    
    loader.clear_documents()
    
    assert loader.documents == []


def test_clear_alias(loader):
    """Test clear method (alias for clear_documents)."""
    loader.documents = [{"content": "test"}]
    
    loader.clear()
    
    assert loader.documents == []


@pytest.mark.asyncio
async def test_load_documents_async(loader):
    """Test async load_documents method."""
    test_files = ["/test/file1.txt", "/test/file2.json"]
    
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(loader, '_load_file') as mock_load:
                mock_load.return_value = {
                    'path': '/test/file1.txt',
                    'name': 'file1.txt',
                    'content': 'test content',
                    'type': 'txt'
                }
                
                docs = await loader.load_documents(test_files)
                
                assert len(docs) == 2
                assert mock_load.call_count == 2


@pytest.mark.asyncio
async def test_load_documents_directory(loader):
    """Test loading documents from directory."""
    with patch.object(Path, 'exists', return_value=True):
        with patch.object(Path, 'is_dir', return_value=True):
            with patch.object(Path, 'rglob') as mock_rglob:
                mock_files = [
                    MagicMock(suffix='.txt'),
                    MagicMock(suffix='.json'),
                    MagicMock(suffix='.py')  # Should be skipped
                ]
                mock_rglob.return_value = mock_files
                
                with patch.object(loader, '_load_file') as mock_load:
                    mock_load.return_value = {'content': 'test'}
                    
                    docs = await loader.load_documents(["/test/dir"])
                    
                    # Should only load supported extensions
                    assert mock_load.call_count == 2


@pytest.mark.asyncio
async def test_load_file_async(loader):
    """Test async _load_file method."""
    test_path = Path("/test/file.json")
    test_data = {"key": "value"}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
        result = await loader._load_file(test_path)
        
    assert result is not None
    assert result['path'] == str(test_path)
    assert result['name'] == "file.json"
    assert result['type'] == 'json'
    assert result['content'] == test_data


@pytest.mark.asyncio
async def test_load_file_yaml(loader):
    """Test loading YAML file."""
    test_path = Path("/test/file.yaml")
    test_data = {"config": {"key": "value"}}
    
    with patch('builtins.open', mock_open(read_data=yaml.dump(test_data))):
        result = await loader._load_file(test_path)
        
    assert result is not None
    assert result['content'] == test_data
    assert result['type'] == 'yaml'


@pytest.mark.asyncio
async def test_load_file_text_async(loader):
    """Test loading text file asynchronously."""
    test_path = Path("/test/file.txt")
    test_content = "Plain text content"
    
    with patch('builtins.open', mock_open(read_data=test_content)):
        result = await loader._load_file(test_path)
        
    assert result is not None
    assert result['content'] == test_content
    assert result['type'] == 'txt'


@pytest.mark.asyncio
async def test_load_file_async_error(loader):
    """Test async file loading with error."""
    test_path = Path("/test/file.txt")
    
    with patch('builtins.open', side_effect=Exception("Read error")):
        with patch('builtins.print') as mock_print:
            result = await loader._load_file(test_path)
            
    assert result is None
    mock_print.assert_called_once()


def test_load_file_json_malformed(loader):
    """Test loading malformed JSON file."""
    with patch('builtins.open', mock_open(read_data="not valid json")):
        with patch('json.load', side_effect=json.JSONDecodeError("test", "doc", 0)):
            result = loader.load_file("test.json")
            
    assert result is None


def test_split_documents_single_char_chunks(loader):
    """Test splitting with very small chunks."""
    loader.documents = [{"content": "ABCDEF", "source": "test.txt"}]
    
    chunks = loader.split_documents(chunk_size=1)
    
    assert len(chunks) == 6
    assert all(len(chunk['content']) == 1 for chunk in chunks)


def test_split_documents_preserve_source(loader):
    """Test that split chunks preserve source information."""
    loader.documents = [
        {"content": "A" * 100, "source": "doc1.txt"},
        {"content": "B" * 100, "source": "doc2.txt"}
    ]
    
    chunks = loader.split_documents(chunk_size=50)
    
    # Check that source is preserved
    doc1_chunks = [c for c in chunks if c['source'] == 'doc1.txt']
    doc2_chunks = [c for c in chunks if c['source'] == 'doc2.txt']
    
    assert len(doc1_chunks) == 2
    assert len(doc2_chunks) == 2


def test_extract_metadata_with_colons_in_value(loader):
    """Test metadata extraction with colons in values."""
    content = """URL: https://example.com:8080
Time: 10:30:45
Content starts here"""
    
    metadata = loader.extract_metadata(content)
    
    assert metadata['url'] == "https://example.com:8080"
    assert metadata['time'] == "10:30:45"


def test_load_directory_empty(loader):
    """Test loading empty directory."""
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = []
        
        loader.load_directory("/empty/dir")
        
    assert len(loader.documents) == 0


def test_supported_extensions_comprehensive(loader):
    """Test all supported extensions."""
    extensions = loader.supported_extensions
    
    assert '.txt' in extensions
    assert '.md' in extensions
    assert '.json' in extensions
    assert '.yaml' in extensions
    assert '.yml' in extensions
    assert len(extensions) == 5