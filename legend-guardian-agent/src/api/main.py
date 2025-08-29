"""FastAPI main application."""

import time
from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
try:
    from opentelemetry import trace  # type: ignore
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
    _OTEL_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    trace = None  # type: ignore
    FastAPIInstrumentor = None  # type: ignore
    _OTEL_AVAILABLE = False

from src.api.routers import (
    adapters_depot,
    adapters_engine,
    adapters_sdlc,
    flows,
    health,
    intent,
    webhooks,
)
from src.settings import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        structlog.processors.dict_tracebacks,
        structlog.development.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Legend Guardian Agent", version=settings.app_version)
    
    # Initialize OpenTelemetry if enabled
    if settings.otel_enabled and _OTEL_AVAILABLE:
        tracer = trace.get_tracer(__name__)  # type: ignore[attr-defined]
        FastAPIInstrumentor.instrument_app(app)  # type: ignore[operator]
        logger.info("OpenTelemetry instrumentation enabled")
    elif settings.otel_enabled and not _OTEL_AVAILABLE:
        logger.warning("OpenTelemetry enabled but not installed; skipping instrumentation")
    
    yield
    
    logger.info("Shutting down Legend Guardian Agent")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade agent for orchestrating FINOS Legend stack operations",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests."""
    correlation_id = request.headers.get("X-Correlation-ID", str(time.time()))
    request.state.correlation_id = correlation_id
    
    with structlog.contextvars.bound_contextvars(correlation_id=correlation_id):
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )
    
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
    )
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        method=request.method,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "hint": "Check logs for details",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(intent.router, prefix="/intent", tags=["Agent"])
app.include_router(adapters_engine.router, prefix="/adapters/engine", tags=["Engine"])
app.include_router(adapters_sdlc.router, prefix="/adapters/sdlc", tags=["SDLC"])
app.include_router(adapters_depot.router, prefix="/adapters/depot", tags=["Depot"])
app.include_router(flows.router, prefix="/flows", tags=["Flows"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
