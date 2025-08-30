import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.rag import store

def test_store_has_expected_methods():
    assert hasattr(store, "VectorStore")
    vs = store.VectorStore()
    assert hasattr(vs, "add_documents")
