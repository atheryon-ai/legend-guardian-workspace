from fastapi import APIRouter, Depends
from src.agent.orchestrator import orchestrator
from src.api.deps import get_api_key
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class IntentPayload(BaseModel):
    prompt: str
    projectId: Optional[str] = None
    workspaceId: Optional[str] = None


@router.post("/intent", dependencies=[Depends(get_api_key)])
async def process_intent(payload: IntentPayload):
    """Process a user intent to generate and execute a plan."""
    plan = await orchestrator.create_plan(
        prompt=payload.prompt,
        project_id=payload.projectId,
        workspace_id=payload.workspaceId,
    )

    execution_result = await orchestrator.execute_plan(
        plan, payload.prompt, payload.projectId, payload.workspaceId
    )

    return {
        "plan": plan.get("steps", []),
        "actions": execution_result.get("artifacts", []),
        "logs": execution_result.get("logs", []),
        "artifacts": execution_result.get("artifacts", []),
    }
