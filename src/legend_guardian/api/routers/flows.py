"""Use case flow endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from legend_guardian.agent.orchestrator import AgentOrchestrator
from legend_guardian.api.deps import get_correlation_id, get_project_id, get_workspace_id, verify_api_key
from legend_guardian.config import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class IngestPublishRequest(BaseModel):
    """Use Case 1: Ingest → Model → Map → Publish Service."""
    
    csv_data: str = Field(..., description="CSV data to ingest")
    model_name: str = Field(..., description="Target model name")
    service_path: str = Field(..., description="Service path to publish")
    mapping_name: str = Field(default="FlatDataMapping", description="Mapping name")


class SafeRolloutRequest(BaseModel):
    """Use Case 2: Model Change with Safe Rollout."""
    
    model_path: str = Field(..., description="Model to change")
    changes: Dict[str, Any] = Field(..., description="Changes to apply")
    keep_v1: bool = Field(True, description="Keep v1 service running")


class ModelReuseRequest(BaseModel):
    """Use Case 3: Cross-bank Model Reuse via Depot."""
    
    search_query: str = Field(..., description="Model search query")
    target_format: str = Field("avro", description="Target format (avro/protobuf)")
    service_name: str = Field(..., description="Service name to create")


class ReverseETLRequest(BaseModel):
    """Use Case 4: Reverse ETL → Data Product."""
    
    source_table: str = Field(..., description="Source database table")
    model_name: str = Field(..., description="Model name to create")
    constraints: List[str] = Field(default_factory=list, description="Constraints to apply")


class GovernanceAuditRequest(BaseModel):
    """Use Case 5: Governance Audit & Lineage Proof."""
    
    scope: str = Field("all", description="Audit scope (all/models/services)")
    include_tests: bool = Field(True, description="Run constraint tests")
    generate_evidence: bool = Field(True, description="Generate evidence bundle")


class ContractFirstRequest(BaseModel):
    """Use Case 6: Contract-first API."""
    
    schema: Dict[str, Any] = Field(..., description="JSON Schema or OpenAPI spec")
    service_path: str = Field(..., description="Service path to create")
    generate_tests: bool = Field(True, description="Generate tests")


class BulkBackfillRequest(BaseModel):
    """Use Case 7: Bulk Backfill & Regression."""
    
    data_source: str = Field(..., description="Data source for backfill")
    window_size: int = Field(1000, description="Processing window size")
    target_model: str = Field(..., description="Target model")
    validate_sample: bool = Field(True, description="Validate sample before full run")


class IncidentRollbackRequest(BaseModel):
    """Use Case 8: Incident Response / Rollback."""
    
    service_path: str = Field(..., description="Service to rollback")
    target_version: Optional[str] = Field(None, description="Target version (or auto-detect)")
    create_hotfix: bool = Field(True, description="Create hotfix workspace")


@router.post("/usecase1/ingest-publish")
async def flow_ingest_publish(
    request: IngestPublishRequest,
    project_id: str = Depends(get_project_id),
    workspace_id: str = Depends(get_workspace_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 1: Ingest → Model → Map → Publish Service.
    
    Complete flow from CSV ingestion to service publication.
    """
    logger.info(
        "Running Use Case 1: Ingest → Publish",
        correlation_id=correlation_id,
        model_name=request.model_name,
        service_path=request.service_path,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        # Execute flow steps
        steps = [
            ("create_workspace", {"project_id": project_id, "workspace_id": workspace_id}),
            ("create_model", {"name": request.model_name, "csv_data": request.csv_data}),
            ("create_mapping", {"name": request.mapping_name, "model": request.model_name}),
            ("compile", {}),
            ("generate_service", {"path": request.service_path}),
            ("open_review", {"title": f"Add {request.model_name} service"}),
        ]
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "ingest_publish",
            "status": "completed",
            "results": results,
            "service_url": f"{settings.engine_url}/api/service/{request.service_path}",
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 1 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase2/safe-rollout")
async def flow_safe_rollout(
    request: SafeRolloutRequest,
    project_id: str = Depends(get_project_id),
    workspace_id: str = Depends(get_workspace_id),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 2: Model Change with Safe Rollout.
    
    Safely roll out model changes with versioning.
    """
    logger.info(
        "Running Use Case 2: Safe Rollout",
        correlation_id=correlation_id,
        model_path=request.model_path,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("create_workspace", {"project_id": project_id, "workspace_id": f"{workspace_id}-v2"}),
            ("apply_changes", {"model_path": request.model_path, "changes": request.changes}),
            ("compile", {}),
            ("run_tests", {}),
            ("create_v2_service", {"keep_v1": request.keep_v1}),
            ("open_review", {"title": f"Safe rollout: {request.model_path} changes"}),
        ]
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "safe_rollout",
            "status": "completed",
            "results": results,
            "v1_maintained": request.keep_v1,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 2 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase3/model-reuse")
async def flow_model_reuse(
    request: ModelReuseRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 3: Cross-bank Model Reuse via Depot.
    
    Reuse models from depot with format transformation.
    """
    logger.info(
        "Running Use Case 3: Model Reuse",
        correlation_id=correlation_id,
        search_query=request.search_query,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("search_depot", {"query": request.search_query}),
            ("import_model", {"format": request.target_format}),
            ("transform_schema", {"format": request.target_format}),
            ("create_service", {"name": request.service_name}),
        ]
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "model_reuse",
            "status": "completed",
            "results": results,
            "schema_format": request.target_format,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 3 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase4/reverse-etl")
async def flow_reverse_etl(
    request: ReverseETLRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 4: Reverse ETL → Data Product.
    
    Create data product from database.
    """
    logger.info(
        "Running Use Case 4: Reverse ETL",
        correlation_id=correlation_id,
        source_table=request.source_table,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("analyze_table", {"table": request.source_table}),
            ("generate_model", {"name": request.model_name}),
            ("add_constraints", {"constraints": request.constraints}),
            ("compile", {}),
            ("create_data_product", {}),
            ("export_schema", {"format": "jsonSchema"}),
        ]
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "reverse_etl",
            "status": "completed",
            "results": results,
            "model_created": request.model_name,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 4 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase5/governance-audit")
async def flow_governance_audit(
    request: GovernanceAuditRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 5: Governance Audit & Lineage Proof.
    
    Comprehensive governance audit with evidence.
    """
    logger.info(
        "Running Use Case 5: Governance Audit",
        correlation_id=correlation_id,
        scope=request.scope,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("enumerate_entities", {"scope": request.scope}),
            ("compile_all", {}),
        ]
        
        if request.include_tests:
            steps.append(("run_constraint_tests", {}))
        
        if request.generate_evidence:
            steps.append(("generate_evidence_bundle", {}))
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "governance_audit",
            "status": "completed",
            "results": results,
            "audit_scope": request.scope,
            "evidence_generated": request.generate_evidence,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 5 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase6/contract-first")
async def flow_contract_first(
    request: ContractFirstRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 6: Contract-first API.
    
    Generate API from schema contract.
    """
    logger.info(
        "Running Use Case 6: Contract-first",
        correlation_id=correlation_id,
        service_path=request.service_path,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("schema_to_model", {"schema": request.schema}),
            ("compile", {}),
        ]
        
        if request.generate_tests:
            steps.extend([
                ("generate_positive_tests", {}),
                ("generate_negative_tests", {}),
            ])
        
        steps.append(("publish_service", {"path": request.service_path}))
        steps.append(("attach_schema_bundle", {}))
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "contract_first",
            "status": "completed",
            "results": results,
            "service_path": request.service_path,
            "tests_generated": request.generate_tests,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 6 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase7/bulk-backfill")
async def flow_bulk_backfill(
    request: BulkBackfillRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 7: Bulk Backfill & Regression.
    
    Execute bulk data backfill with validation.
    """
    logger.info(
        "Running Use Case 7: Bulk Backfill",
        correlation_id=correlation_id,
        data_source=request.data_source,
        target_model=request.target_model,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("plan_ingestion", {
                "source": request.data_source,
                "window_size": request.window_size,
            }),
        ]
        
        if request.validate_sample:
            steps.append(("validate_sample", {"size": 100}))
        
        steps.extend([
            ("execute_backfill", {"target": request.target_model}),
            ("record_manifest", {}),
        ])
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "bulk_backfill",
            "status": "completed",
            "results": results,
            "window_size": request.window_size,
            "sample_validated": request.validate_sample,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 7 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/usecase8/incident-rollback")
async def flow_incident_rollback(
    request: IncidentRollbackRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Use Case 8: Incident Response / Rollback.
    
    Emergency rollback procedure.
    """
    logger.info(
        "Running Use Case 8: Incident Rollback",
        correlation_id=correlation_id,
        service_path=request.service_path,
    )
    
    try:
        orchestrator = AgentOrchestrator(settings=settings)
        
        steps = [
            ("list_versions", {"service": request.service_path}),
        ]
        
        if not request.target_version:
            steps.append(("find_last_good_version", {}))
        
        if request.create_hotfix:
            steps.append(("create_hotfix_workspace", {}))
        
        steps.extend([
            ("revert_to_version", {"version": request.target_version}),
            ("compile", {}),
            ("flip_traffic", {}),
        ])
        
        results = []
        for action, params in steps:
            result = await orchestrator.execute_step(action, params)
            results.append({"action": action, "result": result})
        
        return {
            "use_case": "incident_rollback",
            "status": "completed",
            "results": results,
            "service_path": request.service_path,
            "rolled_back_to": request.target_version,
            "hotfix_created": request.create_hotfix,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Use Case 8 failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
