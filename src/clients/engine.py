
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from src.settings import settings

class LegendEngineClient:
    def __init__(self):
        self.base_url = settings.ENGINE_URL
        self.headers = {"Authorization": f"Bearer {settings.ENGINE_TOKEN}"}
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def compile(self, pure_code: str, project_id: str, workspace_id: str) -> dict:
        """Compile PURE code."""
        try:
            response = await self.client.post(f"/api/pure/v1/compilation/compile?projectId={project_id}&workspaceId={workspace_id}", content=pure_code)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def generate_plan(self, mapping: str, runtime: str, query: str) -> dict:
        """Generate an execution plan."""
        try:
            payload = {
                "query": query,
                "mapping": mapping,
                "runtime": runtime,
                "serializer": "pure"
            }
            response = await self.client.post("/api/pure/v1/execution/execute", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def transform(self, schema_type: str, class_path: str) -> dict:
        """Transform a class to a schema."""
        try:
            payload = {
                "class": class_path,
                "type": schema_type
            }
            response = await self.client.post("/api/pure/v1/schema/generation", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def run_service(self, path: str, params: dict) -> dict:
        """Run a service."""
        try:
            response = await self.client.get(f"/api/service/v1/execute/{path}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def generate_service(self, project_id: str, workspace_id: str, service_path: str, query: str) -> dict:
        """Generate a service."""
        try:
            payload = {
                "path": service_path,
                "query": query
            }
            response = await self.client.post(f"/api/pure/v1/service/generation?projectId={project_id}&workspaceId={workspace_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

engine_client = LegendEngineClient()
