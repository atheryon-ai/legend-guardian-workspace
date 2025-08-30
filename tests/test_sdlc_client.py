import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients import sdlc

def test_sdlc_has_expected_methods():
    assert hasattr(sdlc, "SDLCClient")
    assert hasattr(sdlc.SDLCClient, "__init__")
    assert hasattr(sdlc.SDLCClient, "list_workspaces")
    assert hasattr(sdlc.SDLCClient, "create_workspace")
    assert hasattr(sdlc.SDLCClient, "delete_workspace")
