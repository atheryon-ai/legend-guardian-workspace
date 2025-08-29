"""Intent processing endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.agent.orchestrator import AgentOrchestrator
from src.api.deps import get_correlation_id, get_project_id, get_workspace_id, verify_api_key
from src.settings import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class IntentRequest(BaseModel):
    """Intent request model."""
    
    prompt: str = Field(..., description="Natural language prompt")
    project_id: Optional[str] = Field(None, description="Project ID to use")
    workspace_id: Optional[str] = Field(None, description="Workspace ID to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    execute: bool = Field(True, description="Whether to execute the plan")


class Step(BaseModel):
    """Execution step model."""
    
    id: str
    action: str
    params: Dict[str, Any]
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IntentResponse(BaseModel):
    """Intent response model."""
    
    correlation_id: str
    prompt: str
    plan: List[Step]
    actions: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    logs: List[str]
    status: str
    execution_time_ms: float


@router.post("/", response_model=IntentResponse)
async def process_intent(
    request: IntentRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    project_id: str = Depends(get_project_id),
    workspace_id: str = Depends(get_workspace_id),
    settings: Settings = Depends(get_settings),
) -> IntentResponse:
    """
    Process a natural language intent.
    
    Parses the intent, creates an execution plan, and optionally executes it.
    
    Example prompts:
    - "Create a new Trade model with fields: id, ticker, quantity, price"
    - "Compile and validate the current workspace"
    - "Generate a service that returns trades by ticker"
    - "Open a PR with the current changes"
    """
    import time
    
    start_time = time.time()
    
    logger.info(
        "Processing intent",
        correlation_id=correlation_id,
        prompt=request.prompt[:100],
        project_id=project_id or request.project_id,
        workspace_id=workspace_id or request.workspace_id,
    )
    
    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(settings=settings)
        
        # Parse and plan
        plan = await orchestrator.parse_intent(
            prompt=request.prompt,
            context={
                "project_id": project_id or request.project_id,
                "workspace_id": workspace_id or request.workspace_id,
                "correlation_id": correlation_id,
                **(request.context or {}),
            }
        )
        
        # Convert plan to steps
        steps = [
            Step(
                id=f"step_{i}",
                action=step["action"],
                params=step.get("params", {}),
            )
            for i, step in enumerate(plan)
        ]
        
        actions = []
        artifacts = []
        logs = []
        
        # Execute if requested
        if request.execute:
            for step in steps:
                step.started_at = datetime.utcnow()
                step.status = "running"
                
                try:
                    result = await orchestrator.execute_step(
                        action=step.action,
                        params=step.params,
                    )
                    
                    step.status = "completed"
                    step.result = result
                    step.completed_at = datetime.utcnow()
                    
                    # Collect outputs
                    if result:
                        actions.append({
                            "step_id": step.id,
                            "action": step.action,
                            "result": result,
                        })
                        
                        if isinstance(result, dict):
                            if "artifact" in result:
                                artifacts.append(result["artifact"])
                            if "log" in result:
                                logs.append(result["log"])
                    
                except Exception as e:
                    step.status = "failed"
                    step.error = str(e)
                    step.completed_at = datetime.utcnow()
                    logger.error(f"Step {step.id} failed", error=str(e))
                    
                    if not settings.debug:
                        break  # Stop on first error in production
        
        # Determine overall status
        if not request.execute:
            status = "planned"
        elif all(s.status == "completed" for s in steps):
            status = "completed"
        elif any(s.status == "failed" for s in steps):
            status = "failed"
        else:
            status = "partial"
        
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(
            "Intent processed",
            correlation_id=correlation_id,
            status=status,
            steps_count=len(steps),
            execution_time_ms=execution_time,
        )
        
        return IntentResponse(
            correlation_id=correlation_id,
            prompt=request.prompt,
            plan=steps,
            actions=actions,
            artifacts=artifacts,
            logs=logs,
            status=status,
            execution_time_ms=execution_time,
        )
        
    except Exception as e:
        logger.error("Intent processing failed", error=str(e), correlation_id=correlation_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_intent(
    request: IntentRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Validate an intent without executing it.
    
    Returns the parsed plan and any validation issues.
    """
    logger.info("Validating intent", correlation_id=correlation_id, prompt=request.prompt[:100])
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        plan = await orchestrator.parse_intent(
            prompt=request.prompt,
            context={
                "project_id": request.project_id,
                "workspace_id": request.workspace_id,
                "correlation_id": correlation_id,
                "validate_only": True,
            }
        )
        
        # Validate each step
        validation_results = []
        for i, step in enumerate(plan):
            validation = await orchestrator.validate_step(
                action=step["action"],
                params=step.get("params", {}),
            )
            validation_results.append({
                "step": i,
                "action": step["action"],
                "valid": validation.get("valid", False),
                "issues": validation.get("issues", []),
            })
        
        all_valid = all(v["valid"] for v in validation_results)
        
        return {
            "valid": all_valid,
            "plan": plan,
            "validation": validation_results,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Intent validation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))