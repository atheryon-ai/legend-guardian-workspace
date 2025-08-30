import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.api import main

def test_main_has_expected_methods():
    # Check for FastAPI app and router imports
    assert hasattr(main, "FastAPI")
    assert hasattr(main, "CORSMiddleware")
    assert hasattr(main, "JSONResponse")
