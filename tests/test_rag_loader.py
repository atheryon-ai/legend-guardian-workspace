import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.rag import loader

def test_loader_has_expected_methods():
    assert hasattr(loader, "Loader")
    l = loader.Loader()
    assert hasattr(l, "load_documents")
