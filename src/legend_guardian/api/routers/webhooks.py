"""Webhook endpoints for external integrations."""

from typing import Any, Dict

import structlog
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from legend_guardian.api.deps import get_correlation_id
from legend_guardian.config import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class SDLCWebhookPayload(BaseModel):
    """SDLC webhook payload."""
    
    event_type: str = Field(..., description="Event type (review.created, review.merged, etc.)")
    project_id: str
    workspace_id: str | None = None
    review_id: str | None = None
    user: str
    timestamp: str
    data: Dict[str, Any] = Field(default_factory=dict)


class GitLabWebhookPayload(BaseModel):
    """GitLab webhook payload."""
    
    object_kind: str = Field(..., description="GitLab object kind")
    event_name: str = Field(..., description="Event name")
    project: Dict[str, Any]
    user: Dict[str, Any] | None = None
    object_attributes: Dict[str, Any] | None = None
    repository: Dict[str, Any] | None = None
    commits: list[Dict[str, Any]] | None = None
    merge_request: Dict[str, Any] | None = None


@router.post("/sdlc")
async def handle_sdlc_webhook(
    payload: SDLCWebhookPayload,
    x_sdlc_signature: str | None = Header(None),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Handle SDLC webhook events.
    
    Processes events from Legend SDLC:
    - review.created: New review opened
    - review.merged: Review merged
    - review.closed: Review closed
    - workspace.created: New workspace created
    - version.created: New version tagged
    """
    logger.info(
        "SDLC webhook received",
        correlation_id=correlation_id,
        event_type=payload.event_type,
        project_id=payload.project_id,
        review_id=payload.review_id,
    )
    
    try:
        # Validate signature if configured
        if settings.sdlc_token and x_sdlc_signature:
            # Implement signature validation here
            pass
        
        # Process based on event type
        result = {"processed": False, "action": None}
        
        if payload.event_type == "review.created":
            # Auto-compile and test new reviews
            logger.info("Processing new review", review_id=payload.review_id)
            result = {
                "processed": True,
                "action": "compile_and_test",
                "review_id": payload.review_id,
            }
            
        elif payload.event_type == "review.merged":
            # Deploy service after merge
            logger.info("Processing merged review", review_id=payload.review_id)
            result = {
                "processed": True,
                "action": "deploy_service",
                "review_id": payload.review_id,
            }
            
        elif payload.event_type == "version.created":
            # Publish to depot on version creation
            logger.info("Processing new version", version=payload.data.get("version"))
            result = {
                "processed": True,
                "action": "publish_to_depot",
                "version": payload.data.get("version"),
            }
        
        return {
            "status": "ok",
            "event_type": payload.event_type,
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("SDLC webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gitlab")
async def handle_gitlab_webhook(
    payload: GitLabWebhookPayload = Body(...),
    x_gitlab_token: str | None = Header(None),
    x_gitlab_event: str | None = Header(None),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Handle GitLab webhook events.
    
    Processes events from GitLab:
    - push: Code pushed to repository
    - merge_request: MR created/updated/merged
    - pipeline: Pipeline status change
    - issue: Issue created/updated
    - tag_push: New tag created
    """
    logger.info(
        "GitLab webhook received",
        correlation_id=correlation_id,
        object_kind=payload.object_kind,
        event_name=payload.event_name,
        project=payload.project.get("name") if payload.project else None,
    )
    
    try:
        # Validate token if configured
        if settings.sdlc_token and x_gitlab_token != settings.sdlc_token:
            logger.warning("Invalid GitLab webhook token")
            raise HTTPException(status_code=401, detail="Invalid webhook token")
        
        # Process based on object kind
        result = {"processed": False, "action": None}
        
        if payload.object_kind == "push":
            # Handle push events
            commits = payload.commits or []
            logger.info(f"Processing push with {len(commits)} commits")
            result = {
                "processed": True,
                "action": "validate_commits",
                "commit_count": len(commits),
            }
            
        elif payload.object_kind == "merge_request":
            # Handle merge request events
            mr = payload.merge_request or payload.object_attributes or {}
            state = mr.get("state")
            
            if state == "opened":
                logger.info("Processing new merge request", mr_id=mr.get("iid"))
                result = {
                    "processed": True,
                    "action": "compile_and_comment",
                    "mr_id": mr.get("iid"),
                }
            elif state == "merged":
                logger.info("Processing merged MR", mr_id=mr.get("iid"))
                result = {
                    "processed": True,
                    "action": "trigger_deployment",
                    "mr_id": mr.get("iid"),
                }
            
        elif payload.object_kind == "pipeline":
            # Handle pipeline events
            pipeline = payload.object_attributes or {}
            status = pipeline.get("status")
            
            logger.info("Processing pipeline event", status=status)
            if status == "success":
                result = {
                    "processed": True,
                    "action": "promote_artifact",
                    "pipeline_id": pipeline.get("id"),
                }
            elif status == "failed":
                result = {
                    "processed": True,
                    "action": "notify_failure",
                    "pipeline_id": pipeline.get("id"),
                }
        
        elif payload.object_kind == "tag_push":
            # Handle tag push events
            logger.info("Processing tag push")
            result = {
                "processed": True,
                "action": "create_release",
                "tag": payload.object_attributes.get("ref") if payload.object_attributes else None,
            }
        
        return {
            "status": "ok",
            "object_kind": payload.object_kind,
            "event": x_gitlab_event,
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GitLab webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom/{webhook_id}")
async def handle_custom_webhook(
    webhook_id: str,
    payload: Dict[str, Any] = Body(...),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Handle custom webhook events.
    
    Generic webhook handler for custom integrations.
    """
    logger.info(
        "Custom webhook received",
        correlation_id=correlation_id,
        webhook_id=webhook_id,
        payload_keys=list(payload.keys()),
    )
    
    try:
        # Process based on webhook ID
        result = {
            "webhook_id": webhook_id,
            "processed": True,
            "payload_received": True,
        }
        
        # Add custom processing logic here based on webhook_id
        if webhook_id == "deployment":
            result["action"] = "trigger_deployment"
        elif webhook_id == "monitoring":
            result["action"] = "process_alert"
        else:
            result["action"] = "logged_only"
        
        return {
            "status": "ok",
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Custom webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))