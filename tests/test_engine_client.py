
import pytest
from src.clients.engine import engine_client

@pytest.mark.asyncio
async def test_compile():
    response = await engine_client.compile("test code")
    assert response == {"status": "success", "message": "Code compiled successfully"}

@pytest.mark.asyncio
async def test_generate_plan():
    response = await engine_client.generate_plan("mapping", "runtime", "query")
    assert response == {"status": "success", "plan": {}}

@pytest.mark.asyncio
async def test_transform():
    response = await engine_client.transform("jsonSchema", "classPath")
    assert response == {"status": "success", "schema": {}}

@pytest.mark.asyncio
async def test_run_service():
    response = await engine_client.run_service("path", {})
    assert response == {"status": "success", "result": {}}
