"""Legend SDLC adapter endpoints."""

from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import BaseModel, Field

from src.api.deps import get_correlation_id, get_project_id, get_workspace_id, verify_api_key
from src.clients.sdlc import SDLCClient
from src.settings import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class Entity(BaseModel):
    """SDLC entity model."""
    
    path: str = Field(..., description="Entity path")
    classifier_path: str = Field(..., description="Classifier path (e.g., meta::pure::metamodel::type::Class)")
    content: Dict[str, Any] = Field(..., description="Entity content")


class EntitiesRequest(BaseModel):
    """Entities upsert request."""
    
    replace: bool = Field(False, description="Replace all entities (vs merge)")
    entities: List[Entity] = Field(..., description="Entities to upsert")


class ReviewRequest(BaseModel):
    """Review creation request."""
    
    title: str = Field(..., description="Review title")
    description: str = Field(..., description="Review description")
    workspace_id: str | None = None
    labels: List[str] = Field(default_factory=list, description="Review labels")


class VersionRequest(BaseModel):
    """Version creation request."""
    
    version_id: str = Field(..., description="Version identifier")
    notes: str = Field(..., description="Version notes")
    review_id: str | None = Field(None, description="Associated review ID")


@router.get("/projects")
async def list_projects(
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """
    List all SDLC projects.
    
    Returns available projects with their metadata.
    """
    logger.info("Listing projects", correlation_id=correlation_id)
    
    try:
        client = SDLCClient(settings=settings)
        projects = await client.list_projects()
        
        return projects
        
    except Exception as e:
        logger.error("Failed to list projects", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str = Path(..., description="Project ID"),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Get project details."""
    logger.info("Getting project", correlation_id=correlation_id, project_id=project_id)
    
    try:
        client = SDLCClient(settings=settings)
        project = await client.get_project(project_id)
        
        return project
        
    except Exception as e:
        logger.error("Failed to get project", error=str(e), project_id=project_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workspaces/{workspace_id}")
async def create_workspace(
    workspace_id: str = Path(..., description="Workspace ID"),
    project_id: str = Depends(get_project_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Create a new workspace.
    
    Creates a workspace for making changes to the project.
    """
    logger.info(
        "Creating workspace",
        correlation_id=correlation_id,
        project_id=project_id,
        workspace_id=workspace_id,
    )
    
    try:
        client = SDLCClient(settings=settings)
        workspace = await client.create_workspace(
            project_id=project_id,
            workspace_id=workspace_id,
        )
        
        return workspace
        
    except Exception as e:
        logger.error("Failed to create workspace", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspaces")
async def list_workspaces(
    project_id: str = Depends(get_project_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """List all workspaces for a project."""
    logger.info("Listing workspaces", correlation_id=correlation_id, project_id=project_id)
    
    try:
        client = SDLCClient(settings=settings)
        workspaces = await client.list_workspaces(project_id)
        
        return workspaces
        
    except Exception as e:
        logger.error("Failed to list workspaces", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entities")
async def upsert_entities(
    request: EntitiesRequest,
    project_id: str = Depends(get_project_id),
    workspace_id: str = Depends(get_workspace_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Upsert entities to a workspace.
    
    Add or update entities in the specified workspace.
    """
    logger.info(
        "Upserting entities",
        correlation_id=correlation_id,
        project_id=project_id,
        workspace_id=workspace_id,
        entity_count=len(request.entities),
        replace=request.replace,
    )
    
    try:
        client = SDLCClient(settings=settings)
        result = await client.upsert_entities(
            project_id=project_id,
            workspace_id=workspace_id,
            entities=[e.dict() for e in request.entities],
            replace=request.replace,
        )
        
        return {
            "project_id": project_id,
            "workspace_id": workspace_id,
            "entities_processed": len(request.entities),
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Failed to upsert entities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities")
async def get_entities(
    project_id: str = Depends(get_project_id),
    workspace_id: str = Depends(get_workspace_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """Get all entities in a workspace."""
    logger.info(
        "Getting entities",
        correlation_id=correlation_id,
        project_id=project_id,
        workspace_id=workspace_id,
    )
    
    try:
        client = SDLCClient(settings=settings)
        entities = await client.get_entities(
            project_id=project_id,
            workspace_id=workspace_id,
        )
        
        return entities
        
    except Exception as e:
        logger.error("Failed to get entities", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews")
async def create_review(
    request: ReviewRequest,
    project_id: str = Depends(get_project_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Create a review/PR.
    
    Opens a review for the changes in the workspace.
    """
    workspace_id = request.workspace_id or settings.workspace_id
    
    logger.info(
        "Creating review",
        correlation_id=correlation_id,
        project_id=project_id,
        workspace_id=workspace_id,
        title=request.title,
    )
    
    try:
        client = SDLCClient(settings=settings)
        review = await client.create_review(
            project_id=project_id,
            workspace_id=workspace_id,
            title=request.title,
            description=request.description,
            labels=request.labels,
        )
        
        return review
        
    except Exception as e:
        logger.error("Failed to create review", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews")
async def list_reviews(
    project_id: str = Depends(get_project_id),
    state: str = "open",
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """List reviews for a project."""
    logger.info(
        "Listing reviews",
        correlation_id=correlation_id,
        project_id=project_id,
        state=state,
    )
    
    try:
        client = SDLCClient(settings=settings)
        reviews = await client.list_reviews(
            project_id=project_id,
            state=state,
        )
        
        return reviews
        
    except Exception as e:
        logger.error("Failed to list reviews", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions")
async def create_version(
    request: VersionRequest,
    project_id: str = Depends(get_project_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Create a new version.
    
    Tags a version of the project after review approval.
    """
    logger.info(
        "Creating version",
        correlation_id=correlation_id,
        project_id=project_id,
        version_id=request.version_id,
    )
    
    try:
        client = SDLCClient(settings=settings)
        version = await client.create_version(
            project_id=project_id,
            version_id=request.version_id,
            notes=request.notes,
            review_id=request.review_id,
        )
        
        return version
        
    except Exception as e:
        logger.error("Failed to create version", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/versions")
async def list_versions(
    project_id: str = Depends(get_project_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> List[Dict[str, Any]]:
    """List all versions of a project."""
    logger.info("Listing versions", correlation_id=correlation_id, project_id=project_id)
    
    try:
        client = SDLCClient(settings=settings)
        versions = await client.list_versions(project_id)
        
        return versions
        
    except Exception as e:
        logger.error("Failed to list versions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))