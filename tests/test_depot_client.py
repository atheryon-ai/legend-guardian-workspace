import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from legend_guardian.clients import depot

def test_depot_has_expected_methods():
    assert hasattr(depot, "DepotClient")
    assert hasattr(depot.DepotClient, "__init__")
    assert hasattr(depot.DepotClient, "get_project")
    assert hasattr(depot.DepotClient, "list_projects")
    assert hasattr(depot.DepotClient, "search")
    assert hasattr(depot.DepotClient, "publish")
