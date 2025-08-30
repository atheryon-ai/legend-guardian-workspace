
from fastapi import APIRouter, Depends, Body
from src.clients.sdlc import sdlc_client
from src.api.deps import get_api_key
from pydantic import BaseModel
from typing import List, Dict, Optional

router = APIRouter()

class EntitiesPayload(BaseModel):
    replace: bool = False
    entities: List[Dict]

class ReviewPayload(BaseModel):
    title: str
    description: str

@router.get("/adapters/sdlc/projects", dependencies=[Depends(get_api_key)])
async def list_projects():
    return await sdlc_client.list_projects()

@router.post("/adapters/sdlc/workspaces/{workspace_id}", dependencies=[Depends(get_api_key)])
async def create_workspace(project_id: str, workspace_id: str):
    return await sdlc_client.create_workspace(project_id, workspace_id)

@router.post("/adapters/sdlc/entities", dependencies=[Depends(get_api_key)])
async def upsert_entities(project_id: str, workspace_id: str, payload: EntitiesPayload):
    return await sdlc_client.upsert_entities(project_id, workspace_id, payload.entities, payload.replace)

@router.post("/adapters/sdlc/reviews", dependencies=[Depends(get_api_key)])
async def open_review(project_id: str, workspace_id: str, payload: ReviewPayload):
    return await sdlc_client.open_review(project_id, workspace_id, payload.title, payload.description)
