
import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from src.settings import settings
from typing import List, Dict

class LegendSdlcClient:
    def __init__(self):
        self.base_url = settings.SDLC_URL
        self.headers = {"Authorization": f"Bearer {settings.SDLC_TOKEN}"}
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def list_projects(self) -> List[Dict]:
        """List all projects."""
        try:
            response = await self.client.get("/projects")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_entities(self, project_id: str, workspace_id: str) -> List[Dict]:
        """Get all entities in a workspace."""
        try:
            response = await self.client.get(f"/projects/{project_id}/workspaces/{workspace_id}/entities")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def create_workspace(self, project_id: str, workspace_id: str) -> dict:
        """Create a new workspace."""
        try:
            response = await self.client.post(f"/projects/{project_id}/workspaces/{workspace_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def upsert_entities(self, project_id: str, workspace_id: str, entities: List[Dict], replace: bool = False) -> dict:
        """Upsert entities in a workspace."""
        try:
            payload = {"replace": replace, "entities": entities}
            response = await self.client.post(f"/projects/{project_id}/workspaces/{workspace_id}/entities", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def open_review(self, project_id: str, workspace_id: str, title: str, description: str) -> dict:
        """Open a review for a workspace."""
        try:
            payload = {"title": title, "description": description}
            response = await self.client.post(f"/projects/{project_id}/workspaces/{workspace_id}/review", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def create_version(self, project_id: str, version_id: str, notes: str) -> dict:
        """Create a new version of a project."""
        try:
            payload = {"notes": notes}
            response = await self.client.post(f"/projects/{project_id}/versions/{version_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"status": "error", "message": str(e)}

sdlc_client = LegendSdlcClient()
