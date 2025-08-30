"""Legend Engine adapter endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from legend_guardian.api.deps import get_correlation_id, verify_api_key
from legend_guardian.clients.engine import EngineClient
from legend_guardian.config import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


class CompileRequest(BaseModel):
    """PURE compilation request."""
    
    pure: str = Field(..., description="PURE code to compile")
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None


class CompileResponse(BaseModel):
    """Compilation response."""
    
    ok: bool
    details: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None


class ExecutionPlanRequest(BaseModel):
    """Execution plan request."""
    
    mapping: str = Field(..., description="Mapping path")
    runtime: str = Field(..., description="Runtime path")
    query: str = Field(..., description="Query to execute")


class TransformRequest(BaseModel):
    """Schema transformation request."""
    
    class_path: str = Field(..., description="Class path to transform")
    include_dependencies: bool = Field(False, description="Include dependencies")


@router.post("/compile", response_model=CompileResponse)
async def compile_pure(
    request: CompileRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> CompileResponse:
    """
    Compile PURE code.
    
    Validates PURE syntax and returns compilation results.
    """
    logger.info("Compiling PURE", correlation_id=correlation_id, size=len(request.pure))
    
    try:
        client = EngineClient(settings=settings)
        result = await client.compile(
            pure=request.pure,
            project_id=request.project_id,
            workspace_id=request.workspace_id,
        )
        
        if result.get("status") == "success":
            return CompileResponse(ok=True, details=result.get("details"))
        else:
            return CompileResponse(ok=False, errors=result.get("errors", []))
            
    except Exception as e:
        logger.error("Compilation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execution-plan")
async def generate_execution_plan(
    request: ExecutionPlanRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Generate execution plan for a query.
    
    Creates an optimized execution plan for the given mapping, runtime, and query.
    """
    logger.info(
        "Generating execution plan",
        correlation_id=correlation_id,
        mapping=request.mapping,
        runtime=request.runtime,
    )
    
    try:
        client = EngineClient(settings=settings)
        plan = await client.generate_execution_plan(
            mapping=request.mapping,
            runtime=request.runtime,
            query=request.query,
        )
        
        return {
            "plan": plan,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Failed to generate execution plan", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transform/{schema_type}")
async def transform_to_schema(
    schema_type: Literal["jsonSchema", "avro", "protobuf"],
    request: TransformRequest,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Transform a class to a schema format.
    
    Converts a Legend class to JSON Schema, Avro, or Protobuf format.
    """
    logger.info(
        "Transforming to schema",
        correlation_id=correlation_id,
        schema_type=schema_type,
        class_path=request.class_path,
    )
    
    try:
        client = EngineClient(settings=settings)
        schema = await client.transform_to_schema(
            schema_type=schema_type,
            class_path=request.class_path,
            include_dependencies=request.include_dependencies,
        )
        
        return {
            "schema_type": schema_type,
            "class_path": request.class_path,
            "schema": schema,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Schema transformation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/service/run")
async def run_service(
    path: str,
    params: Dict[str, Any] = Body(default={}),
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Run a Legend service.
    
    Executes a service with the given parameters and returns results.
    """
    logger.info(
        "Running service",
        correlation_id=correlation_id,
        path=path,
        params=list(params.keys()),
    )
    
    try:
        client = EngineClient(settings=settings)
        result = await client.run_service(
            path=path,
            params=params,
        )
        
        return {
            "path": path,
            "result": result,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Service execution failed", error=str(e), path=path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/run")
async def run_tests(
    test_path: Optional[str] = None,
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Run Legend tests.
    
    Executes tests and returns results with pass/fail status.
    """
    logger.info("Running tests", correlation_id=correlation_id, test_path=test_path)
    
    try:
        client = EngineClient(settings=settings)
        results = await client.run_tests(test_path=test_path)
        
        return {
            "test_path": test_path,
            "results": results,
            "passed": all(r.get("passed", False) for r in results),
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Test execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_engine_info(
    api_key: str = Depends(verify_api_key),
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Get Legend Engine information and version."""
    try:
        client = EngineClient(settings=settings)
        info = await client.get_info()
        
        return {
            **info,
            "correlation_id": correlation_id,
        }
        
    except Exception as e:
        logger.error("Failed to get engine info", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
