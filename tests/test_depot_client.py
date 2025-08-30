import pytest
from src.clients.depot import depot_client


@pytest.mark.asyncio
async def test_search():
    response = await depot_client.search("query")
    assert response == []


@pytest.mark.asyncio
async def test_list_versions():
    response = await depot_client.list_versions("project_id")
    assert response == []


@pytest.mark.asyncio
async def test_get_entities():
    response = await depot_client.get_entities("project_id", "version")
    assert response == []
