"""Legend Depot client implementation."""

from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.settings import Settings

logger = structlog.get_logger()


class DepotClient:
    """Client for Legend Depot API."""
    
    def __init__(self, settings: Settings):
        """Initialize Depot client."""
        self.settings = settings
        self.base_url = settings.depot_url
        self.timeout = httpx.Timeout(settings.request_timeout)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if settings.depot_token:
            self.headers["Authorization"] = f"Bearer {settings.depot_token}"
    
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
        """Make HTTP request to Depot."""
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
                "Depot request",
                method=method,
                path=path,
                status=response.status_code,
            )
            
            if response.status_code >= 400:
                error_detail = response.text
                logger.error(
                    "Depot request failed",
                    status=response.status_code,
                    error=error_detail,
                )
                raise Exception(f"Depot API error: {response.status_code} - {error_detail}")
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return response.text
    
    async def get_info(self) -> Dict[str, Any]:
        """Get Depot server information."""
        return await self._request("GET", "/api/info")
    
    async def search(
        self,
        query: str,
        limit: int = 20,
        project_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search depot for models.
        
        Args:
            query: Search query
            limit: Maximum results
            project_filter: Optional project filter
        
        Returns:
            Search results
        """
        logger.info("Searching depot", query=query, limit=limit)
        
        params = {
            "q": query,
            "limit": limit,
        }
        
        if project_filter:
            params["project"] = project_filter
        
        return await self._request(
            "GET",
            "/api/search",
            params=params,
        )
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all depot projects.
        
        Returns:
            List of projects with metadata
        """
        logger.info("Listing depot projects")
        return await self._request("GET", "/api/projects")
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get depot project details.
        
        Args:
            project_id: Project identifier
        
        Returns:
            Project details
        """
        logger.info("Getting depot project", project_id=project_id)
        return await self._request("GET", f"/api/projects/{project_id}")
    
    async def list_versions(
        self,
        project_id: str,
        limit: int = 50,
    ) -> List[str]:
        """
        List versions for a depot project.
        
        Args:
            project_id: Project identifier
            limit: Maximum results
        
        Returns:
            List of version identifiers
        """
        logger.info("Listing project versions", project_id=project_id)
        
        result = await self._request(
            "GET",
            f"/api/projects/{project_id}/versions",
            params={"limit": limit},
        )
        
        # Extract version IDs from response
        if isinstance(result, list):
            return [v.get("version", v) if isinstance(v, dict) else v for v in result]
        return result.get("versions", [])
    
    async def get_latest_version(self, project_id: str) -> str:
        """
        Get latest version of a project.
        
        Args:
            project_id: Project identifier
        
        Returns:
            Latest version identifier
        """
        logger.info("Getting latest version", project_id=project_id)
        
        result = await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/latest",
        )
        
        if isinstance(result, dict):
            return result.get("version", result.get("versionId"))
        return result
    
    async def get_entities(
        self,
        project_id: str,
        version: str,
        entity_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get entities for a project version.
        
        Args:
            project_id: Project identifier
            version: Version identifier
            entity_filter: Optional entity type filter
        
        Returns:
            List of entities
        """
        logger.info(
            "Getting project entities",
            project_id=project_id,
            version=version,
        )
        
        params = {}
        if entity_filter:
            params["type"] = entity_filter
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/{version}/entities",
            params=params,
        )
    
    async def get_entity(
        self,
        project_id: str,
        version: str,
        entity_path: str,
    ) -> Dict[str, Any]:
        """
        Get a specific entity.
        
        Args:
            project_id: Project identifier
            version: Version identifier
            entity_path: Entity path
        
        Returns:
            Entity details
        """
        logger.info(
            "Getting entity",
            project_id=project_id,
            version=version,
            entity_path=entity_path,
        )
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/{version}/entities/{entity_path}",
        )
    
    async def get_dependencies(
        self,
        project_id: str,
        version: str,
        transitive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get dependencies for a project version.
        
        Args:
            project_id: Project identifier
            version: Version identifier
            transitive: Include transitive dependencies
        
        Returns:
            List of dependencies
        """
        logger.info(
            "Getting dependencies",
            project_id=project_id,
            version=version,
            transitive=transitive,
        )
        
        params = {"transitive": transitive}
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/{version}/dependencies",
            params=params,
        )
    
    async def get_dependents(
        self,
        project_id: str,
        version: str,
    ) -> List[Dict[str, Any]]:
        """
        Get projects that depend on this version.
        
        Args:
            project_id: Project identifier
            version: Version identifier
        
        Returns:
            List of dependent projects
        """
        logger.info(
            "Getting dependents",
            project_id=project_id,
            version=version,
        )
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/{version}/dependents",
        )
    
    async def publish(
        self,
        project_id: str,
        version: str,
        entities: Optional[List[Dict[str, Any]]] = None,
        dependencies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Publish a project version to depot.
        
        Args:
            project_id: Project identifier
            version: Version identifier
            entities: Optional entities to publish
            dependencies: Optional dependencies
        
        Returns:
            Publish result
        """
        logger.info(
            "Publishing to depot",
            project_id=project_id,
            version=version,
        )
        
        request_data = {
            "projectId": project_id,
            "version": version,
        }
        
        if entities:
            request_data["entities"] = entities
        
        if dependencies:
            request_data["dependencies"] = dependencies
        
        return await self._request(
            "POST",
            "/api/projects/publish",
            json_data=request_data,
        )
    
    async def get_metadata(
        self,
        project_id: str,
        version: str,
    ) -> Dict[str, Any]:
        """
        Get metadata for a project version.
        
        Args:
            project_id: Project identifier
            version: Version identifier
        
        Returns:
            Version metadata
        """
        logger.info(
            "Getting version metadata",
            project_id=project_id,
            version=version,
        )
        
        return await self._request(
            "GET",
            f"/api/projects/{project_id}/versions/{version}/metadata",
        )
    
    async def resolve_coordinates(
        self,
        group_id: str,
        artifact_id: str,
        version: str,
    ) -> Dict[str, Any]:
        """
        Resolve Maven coordinates to depot project.
        
        Args:
            group_id: Maven group ID
            artifact_id: Maven artifact ID
            version: Version
        
        Returns:
            Resolved project details
        """
        logger.info(
            "Resolving coordinates",
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
        )
        
        return await self._request(
            "GET",
            f"/api/coordinates/{group_id}/{artifact_id}/{version}",
        )