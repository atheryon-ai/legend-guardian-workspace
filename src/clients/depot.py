import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from src.settings import settings
from typing import List, Dict


class LegendDepotClient:
    def __init__(self):
        self.base_url = settings.DEPOT_URL
        self.headers = {"Authorization": f"Bearer {settings.DEPOT_TOKEN}"}
        self.client = httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=30.0
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def search(self, query: str) -> List[Dict]:
        """Search for projects in Depot."""
        try:
            response = await self.client.get("/projects", params={"search": query})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def list_versions(self, project_id: str) -> List[str]:
        """List all versions of a project."""
        try:
            group_id, artifact_id = project_id.split(":")
            response = await self.client.get(
                f"/projects/{group_id}/{artifact_id}/versions"
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, ValueError):
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_entities(self, project_id: str, version: str) -> List[Dict]:
        """Get entities for a specific version of a project."""
        try:
            group_id, artifact_id = project_id.split(":")
            response = await self.client.get(
                f"/projects/{group_id}/{artifact_id}/versions/{version}/entities"
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, ValueError):
            return []


depot_client = LegendDepotClient()
