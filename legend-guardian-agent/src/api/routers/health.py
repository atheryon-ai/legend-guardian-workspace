"""Health check endpoints."""

import asyncio
from typing import Any, Dict

import httpx
import structlog
from fastapi import APIRouter, Depends

from src.api.deps import get_correlation_id
from src.settings import Settings, get_settings

router = APIRouter()
logger = structlog.get_logger()


async def check_service_health(url: str, path: str = "/", timeout: float = 5.0) -> Dict[str, Any]:
    """Check health of a service."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{url}{path}")
            return {
                "status": "up" if response.status_code < 500 else "degraded",
                "latency_ms": round(response.elapsed.total_seconds() * 1000, 2),
                "status_code": response.status_code,
            }
    except Exception as e:
        logger.warning(f"Health check failed for {url}", error=str(e))
        return {
            "status": "down",
            "error": str(e),
        }


@router.get("/health")
async def health_check(
    correlation_id: str = Depends(get_correlation_id),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Health check endpoint with dependency status.
    
    Returns the health status of the agent and all dependent services.
    """
    logger.info("Health check requested", correlation_id=correlation_id)
    
    # Check dependent services
    checks = await asyncio.gather(
        check_service_health(settings.engine_url, "/api/server/v1/info"),
        check_service_health(settings.sdlc_url, "/api/info"),
        check_service_health(settings.depot_url, "/api/info"),
        check_service_health(settings.studio_url, "/studio"),
        return_exceptions=True,
    )
    
    services = {
        "engine": checks[0] if not isinstance(checks[0], Exception) else {"status": "down", "error": str(checks[0])},
        "sdlc": checks[1] if not isinstance(checks[1], Exception) else {"status": "down", "error": str(checks[1])},
        "depot": checks[2] if not isinstance(checks[2], Exception) else {"status": "down", "error": str(checks[2])},
        "studio": checks[3] if not isinstance(checks[3], Exception) else {"status": "down", "error": str(checks[3])},
    }
    
    # Determine overall status
    all_up = all(s.get("status") == "up" for s in services.values())
    any_down = any(s.get("status") == "down" for s in services.values())
    
    overall_status = "ok" if all_up else "degraded" if not any_down else "unhealthy"
    
    return {
        "status": overall_status,
        "version": settings.app_version,
        "services": services,
        "correlation_id": correlation_id,
    }


@router.get("/health/live")
async def liveness_probe() -> Dict[str, str]:
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe.
    
    Checks if the service is ready to accept traffic.
    """
    # Quick check of critical services
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            engine_check = await client.get(f"{settings.engine_url}/api/server/v1/info")
            sdlc_check = await client.get(f"{settings.sdlc_url}/api/info")
            
            if engine_check.status_code < 500 and sdlc_check.status_code < 500:
                return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
    
    return {"status": "not_ready"}