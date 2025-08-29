"""Legend Depot adapter endpoints."""

from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from src.api.deps import get_correlation_id, verify_api_key
from src.clients.depot import DepotClient
from src.settings import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class DepotProject(BaseModel):
    """Depot project model."""
    
    project_id: str
    group_id: str
    artifact_id: str
    versions: List[str]
    latest_version: str | None = None
    description: str | None = None


class DepotEntity(BaseModel):
    """Depot entity model."""
    
    path: str
    classifier_path: str
    content: Dict[str, Any]
    project_id: str
    version: str


@router.get("/search")
async def search_depot(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum results"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """
    Search the depot for models.
    
    Searches across all depot projects for matching entities.
    """
    logger.info(
        "Searching depot",
        correlation_id=correlation_id,
        query=q,
        limit=limit,
    )
    
    try:
        client = DepotClient(settings=settings)
        results = await client.search(
            query=q,
            limit=limit,
        )
        
        return results
        
    except Exception as e:
        logger.error("Depot search failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_depot_projects(
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[DepotProject]:
    """
    List all depot projects.
    
    Returns all available projects in the depot.
    """
    logger.info("Listing depot projects", correlation_id=correlation_id)
    
    try:
        client = DepotClient(settings=settings)
        projects = await client.list_projects()
        
        return [DepotProject(**p) for p in projects]
        
    except Exception as e:
        logger.error("Failed to list depot projects", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_depot_project(
    project_id: str = Path(..., description="Project ID"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Get depot project details."""
    logger.info(
        "Getting depot project",
        correlation_id=correlation_id,
        project_id=project_id,
    )
    
    try:
        client = DepotClient(settings=settings)
        project = await client.get_project(project_id)
        
        return project
        
    except Exception as e:
        logger.error("Failed to get depot project", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/versions")
async def list_project_versions(
    project_id: str = Path(..., description="Project ID"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[str]:
    """
    List versions for a depot project.
    
    Returns all available versions of the specified project.
    """
    logger.info(
        "Listing project versions",
        correlation_id=correlation_id,
        project_id=project_id,
    )
    
    try:
        client = DepotClient(settings=settings)
        versions = await client.list_versions(project_id)
        
        return versions
        
    except Exception as e:
        logger.error("Failed to list versions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/versions/{version}/entities")
async def get_project_entities(
    project_id: str = Path(..., description="Project ID"),
    version: str = Path(..., description="Version"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[DepotEntity]:
    """
    Get entities for a specific project version.
    
    Returns all entities in the specified version of the project.
    """
    logger.info(
        "Getting project entities",
        correlation_id=correlation_id,
        project_id=project_id,
        version=version,
    )
    
    try:
        client = DepotClient(settings=settings)
        entities = await client.get_entities(
            project_id=project_id,
            version=version,
        )
        
        return [
            DepotEntity(
                **e,
                project_id=project_id,
                version=version,
            )
            for e in entities
        ]
        
    except Exception as e:
        logger.error("Failed to get entities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/versions/{version}/dependencies")
async def get_project_dependencies(
    project_id: str = Path(..., description="Project ID"),
    version: str = Path(..., description="Version"),
    transitive: bool = Query(False, description="Include transitive dependencies"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Get dependencies for a project version.
    
    Returns dependency tree for the specified version.
    """
    logger.info(
        "Getting project dependencies",
        correlation_id=correlation_id,
        project_id=project_id,
        version=version,
        transitive=transitive,
    )
    
    try:
        client = DepotClient(settings=settings)
        dependencies = await client.get_dependencies(
            project_id=project_id,
            version=version,
            transitive=transitive,
        )
        
        return {
            "project_id": project_id,
            "version": version,
            "dependencies": dependencies,
            "transitive": transitive,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Failed to get dependencies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/publish")
async def publish_to_depot(
    project_id: str = Path(..., description="Project ID"),
    version: str = Body(..., embed=True),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Publish a project version to depot.
    
    Makes the version available for consumption by other projects.
    """
    logger.info(
        "Publishing to depot",
        correlation_id=correlation_id,
        project_id=project_id,
        version=version,
    )
    
    try:
        client = DepotClient(settings=settings)
        result = await client.publish(
            project_id=project_id,
            version=version,
        )
        
        return {
            "project_id": project_id,
            "version": version,
            "published": True,
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Failed to publish to depot", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))