"""Legend SDLC client implementation."""

from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.settings import Settings

logger = structlog.get_logger()


class SDLCClient:
    """Client for Legend SDLC API."""
    
    def __init__(self, settings: Settings):
        """Initialize SDLC client."""
        self.settings = settings
        self.base_url = settings.sdlc_url
        self.timeout = httpx.Timeout(settings.request_timeout)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if settings.sdlc_token:
            self.headers["Authorization"] = f"Bearer {settings.sdlc_token}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request to SDLC."""
        url = f"{self.base_url}{path}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data,
                params=params,
            )
            
            logger.debug(
                "SDLC request",
                method=method,
                path=path,
                status=response.status_code,
            )
            
            if response.status_code >= 400:
                error_detail = response.text
                logger.error(
                    "SDLC request failed",
                    status=response.status_code,
                    error=error_detail,
                )
                raise Exception(f"SDLC API error: {response.status_code} - {error_detail}")
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text
    
    async def get_info(self) -> Dict[str, Any]:
        """Get SDLC server information."""
        return await self._request("GET", "/api/info")
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of projects with metadata
        """
        logger.info("Listing projects")
        return await self._request("GET", "/api/projects")
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get project details.
        
        Args:
            project_id: Project identifier
        
        Returns:
            Project details
        """
        logger.info("Getting project", project_id=project_id)
        return await self._request("GET", f"/api/projects/{project_id}")
    
    async def create_project(
        self,
        project_id: str,
        name: str,
        description: str,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            project_id: Project identifier
            name: Project name
            description: Project description
            tags: Optional tags
        
        Returns:
            Created project details
        """
        logger.info("Creating project", project_id=project_id, name=name)
        
        request_data = {
            "projectId": project_id,
            "name": name,
            "description": description,
            "tags": tags or [],
        }
        
        return await self._request(
            "POST",
            "/api/projects",
            json_data=request_data,
        )
    
    async def list_workspaces(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List workspaces for a project.
        
        Args:
            project_id: Project identifier
        
        Returns:
            List of workspaces
        """
        logger.info("Listing workspaces", project_id=project_id)
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/workspaces",
        )
    
    async def create_workspace(
        self,
        project_id: str,
        workspace_id: str,
        source: str = "HEAD",
    ) -> Dict[str, Any]:
        """
        Create a new workspace.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
            source: Source revision (default HEAD)
        
        Returns:
            Created workspace details
        """
        logger.info(
            "Creating workspace",
            project_id=project_id,
            workspace_id=workspace_id,
        )
        
        request_data = {
            "workspaceId": workspace_id,
            "source": source,
        }
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/workspaces",
            json_data=request_data,
        )
    
    async def delete_workspace(
        self,
        project_id: str,
        workspace_id: str,
    ) -> None:
        """
        Delete a workspace.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
        """
        logger.info(
            "Deleting workspace",
            project_id=project_id,
            workspace_id=workspace_id,
        )
        
        await self._request(
            "DELETE",
            f"/api/projects/{project_id}/workspaces/{workspace_id}",
        )
    
    async def get_entities(
        self,
        project_id: str,
        workspace_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all entities in a workspace.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
        
        Returns:
            List of entities
        """
        logger.info(
            "Getting entities",
            project_id=project_id,
            workspace_id=workspace_id,
        )
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/workspaces/{workspace_id}/entities",
        )
    
    async def upsert_entities(
        self,
        project_id: str,
        workspace_id: str,
        entities: List[Dict[str, Any]],
        replace: bool = False,
    ) -> Dict[str, Any]:
        """
        Upsert entities to a workspace.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
            entities: List of entities to upsert
            replace: Replace all entities (vs merge)
        
        Returns:
            Operation result
        """
        logger.info(
            "Upserting entities",
            project_id=project_id,
            workspace_id=workspace_id,
            count=len(entities),
            replace=replace,
        )
        
        request_data = {
            "entities": entities,
            "replace": replace,
        }
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/workspaces/{workspace_id}/entities",
            json_data=request_data,
        )
    
    async def delete_entity(
        self,
        project_id: str,
        workspace_id: str,
        entity_path: str,
    ) -> None:
        """
        Delete an entity from a workspace.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
            entity_path: Entity path to delete
        """
        logger.info(
            "Deleting entity",
            project_id=project_id,
            workspace_id=workspace_id,
            entity_path=entity_path,
        )
        
        await self._request(
            "DELETE",
            f"/api/projects/{project_id}/workspaces/{workspace_id}/entities/{entity_path}",
        )
    
    async def create_review(
        self,
        project_id: str,
        workspace_id: str,
        title: str,
        description: str,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a review/PR.
        
        Args:
            project_id: Project identifier
            workspace_id: Workspace identifier
            title: Review title
            description: Review description
            labels: Optional labels
        
        Returns:
            Created review details
        """
        logger.info(
            "Creating review",
            project_id=project_id,
            workspace_id=workspace_id,
            title=title,
        )
        
        request_data = {
            "workspaceId": workspace_id,
            "title": title,
            "description": description,
            "labels": labels or [],
        }
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/reviews",
            json_data=request_data,
        )
    
    async def list_reviews(
        self,
        project_id: str,
        state: str = "open",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List reviews for a project.
        
        Args:
            project_id: Project identifier
            state: Review state filter
            limit: Maximum results
        
        Returns:
            List of reviews
        """
        logger.info(
            "Listing reviews",
            project_id=project_id,
            state=state,
        )
        
        params = {
            "state": state,
            "limit": limit,
        }
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/reviews",
            params=params,
        )
    
    async def get_review(
        self,
        project_id: str,
        review_id: str,
    ) -> Dict[str, Any]:
        """
        Get review details.
        
        Args:
            project_id: Project identifier
            review_id: Review identifier
        
        Returns:
            Review details
        """
        logger.info(
            "Getting review",
            project_id=project_id,
            review_id=review_id,
        )
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/reviews/{review_id}",
        )
    
    async def approve_review(
        self,
        project_id: str,
        review_id: str,
    ) -> Dict[str, Any]:
        """
        Approve a review.
        
        Args:
            project_id: Project identifier
            review_id: Review identifier
        
        Returns:
            Updated review details
        """
        logger.info(
            "Approving review",
            project_id=project_id,
            review_id=review_id,
        )
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/reviews/{review_id}/approve",
        )
    
    async def merge_review(
        self,
        project_id: str,
        review_id: str,
    ) -> Dict[str, Any]:
        """
        Merge a review.
        
        Args:
            project_id: Project identifier
            review_id: Review identifier
        
        Returns:
            Merge result
        """
        logger.info(
            "Merging review",
            project_id=project_id,
            review_id=review_id,
        )
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/reviews/{review_id}/merge",
        )
    
    async def create_version(
        self,
        project_id: str,
        version_id: str,
        notes: str,
        review_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new version.
        
        Args:
            project_id: Project identifier
            version_id: Version identifier
            notes: Version notes
            review_id: Associated review ID
        
        Returns:
            Created version details
        """
        logger.info(
            "Creating version",
            project_id=project_id,
            version_id=version_id,
        )
        
        request_data = {
            "versionId": version_id,
            "notes": notes,
        }
        
        if review_id:
            request_data["reviewId"] = review_id
        
        return await self._request(
            "POST",
            f"/api/projects/{project_id}/versions",
            json_data=request_data,
        )
    
    async def list_versions(
        self,
        project_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List versions for a project.
        
        Args:
            project_id: Project identifier
            limit: Maximum results
        
        Returns:
            List of versions
        """
        logger.info("Listing versions", project_id=project_id)
        
        params = {"limit": limit}
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions",
            params=params,
        )