#!/usr/bin/env python3
"""
Legend Guardian Agent API

FastAPI web service for the Legend Guardian Agent.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from ..agent import LegendGuardianAgent
from ..agent.models import ModelChangeEvent
from .models import (
    ModelChangeRequest, ModelValidationRequest, 
    SystemStatusResponse, ModelChangeResponse, ServerInfoResponse, ServiceStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global agent instance
agent: LegendGuardianAgent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent
    
    # Startup
    logger.info("Starting Legend Guardian Agent...")
    
    # Initialize agent
    legend_engine_url = os.getenv("LEGEND_ENGINE_URL", "http://localhost:6300")
    legend_sdlc_url = os.getenv("LEGEND_SDLC_URL", "http://localhost:6100")
    api_key = os.getenv("LEGEND_API_KEY")
    
    try:
        agent = LegendGuardianAgent(
            legend_engine_url=legend_engine_url,
            legend_sdlc_url=legend_sdlc_url,
            api_key=api_key
        )
        logger.info("Legend Guardian Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Legend Guardian Agent: {e}")
        agent = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Legend Guardian Agent...")
    if agent:
        await agent.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Legend Guardian Agent API",
    description="""
    # Legend Guardian Agent API
    
    **FINOS Legend platform monitoring and management system**
    
    ## Overview
    The Legend Guardian Agent provides automated monitoring, validation, and management capabilities for the FINOS Legend platform.
    
    ## Key Features
    - **Model Change Monitoring**: Automatically detects and analyzes model changes
    - **Impact Assessment**: Determines change impact levels (low, medium, high, critical)
    - **Action Planning**: Creates automated action plans based on change analysis
    - **Service Validation**: Validates models and services through Legend Engine
    - **Memory Management**: Maintains history of all agent interactions and decisions
    
    ## Environment
    - **Development**: Local testing and development
    - **Production**: Azure AKS deployment with full monitoring
    
    ## Legend Services
    - **Legend Engine**: Model execution and validation (Port 6060)
    - **Legend SDLC**: Source control and lifecycle management (Port 7070)
    - **Legend Studio**: Web-based modeling interface (Port 9000)
    
    ## Authentication
    All protected endpoints require a valid API key via Bearer token authentication.
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Legend Guardian Agent",
        "url": "https://github.com/atheryon-ai/legend-guardian-workspace",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local Development Server"
        },
        {
            "url": "https://legend-guardian.azure-legend.com",
            "description": "Azure Production Server"
        }
    ],
    tags=[
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Server Info", 
            "description": "Server configuration and environment information"
        },
        {
            "name": "Model Management",
            "description": "Model change handling and validation"
        },
        {
            "name": "Memory",
            "description": "Agent memory and event history"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify API key for protected endpoints"""
    # In production, implement proper API key validation
    api_key = credentials.credentials
    valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
    
    if not valid_keys or valid_keys == [""]:
        # Demo mode - accept any key
        return True
    
    return api_key in valid_keys

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Legend Guardian Agent API"
    }

# Model change handling endpoint
@app.post("/api/v1/model/change", response_model=ModelChangeResponse, tags=["Model Management"])
async def handle_model_change(
    request: ModelChangeRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """Handle a model change event using the Guardian Agent"""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian Agent not available"
        )
    
    try:
        # Create model change event
        event = ModelChangeEvent(
            event_type=request.event_type,
            model_id=request.model_id,
            timestamp=datetime.now(),
            details=request.details
        )
        
        # Handle the event
        result = await agent.handle_model_change(event)
        
        return ModelChangeResponse(
            success=result.success,
            execution_time=result.execution_time,
            errors=result.errors,
            output=result.output,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error handling model change: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Model validation endpoint
@app.post("/api/v1/model/validate", tags=["Model Management"])
async def validate_model(
    request: ModelValidationRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """Validate a specific model"""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian Agent not available"
        )
    
    try:
        # Validate the model using the agent's engine client
        validation_result = await agent.engine_client.validate_model(request.model_id)
        
        return {
            "success": True,
            "validation_result": validation_result,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error validating model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
    
# System status endpoint
@app.get("/api/v1/system/status", response_model=SystemStatusResponse, tags=["Health"])
async def get_system_status(authenticated: bool = Depends(verify_api_key)):
    """Get current system status and agent information"""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian Agent not available"
        )
    
    try:
        status = agent.get_system_status()
        return SystemStatusResponse(**status)
    
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )

# Memory query endpoints
@app.get("/api/v1/memory/events", tags=["Memory"])
async def get_recent_events(
    limit: int = 10,
    authenticated: bool = Depends(verify_api_key)
):
    """Get recent events from agent memory"""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian Agent not available"
        )
    
    try:
        events = agent.memory.get_recent_events(limit)
        return {
            "success": True,
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting recent events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )

@app.get("/api/v1/memory/events/{event_type}", tags=["Memory"])
async def get_events_by_type(
    event_type: str,
    authenticated: bool = Depends(verify_api_key)
):
    """Get events filtered by type"""
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian Agent not available"
        )
    
    try:
        events = agent.memory.get_events_by_type(event_type)
        return {
            "success": True,
            "event_type": event_type,
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting events by type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )

# Root endpoint
@app.get("/", tags=["Server Info"])
async def root():
    """Root endpoint with comprehensive service information"""
    # Get environment information
    environment = "production" if not os.getenv("LEGEND_API_DEBUG", "false").lower() == "true" else "development"
    
    return {
        "service": "Legend Guardian Agent API",
        "version": "1.0.0",
        "description": "API for monitoring and managing the FINOS Legend platform",
        "environment": environment,
        "host": os.getenv("LEGEND_API_HOST", "0.0.0.0"),
        "port": int(os.getenv("LEGEND_API_PORT", "8000")),
        "debug_mode": os.getenv("LEGEND_API_DEBUG", "false").lower() == "true",
        "legend_services": {
            "engine": {
                "name": "Legend Engine",
                "url": os.getenv("LEGEND_ENGINE_URL", "http://localhost:6300"),
                "status": "configured"
            },
            "sdlc": {
                "name": "Legend SDLC", 
                "url": os.getenv("LEGEND_SDLC_URL", "http://localhost:6100"),
                "status": "configured"
            }
        },
        "api_endpoints": {
            "health": "/health",
            "server_info": "/api/v1/server/info",
            "model_change": "/api/v1/model/change",
            "model_validation": "/api/v1/model/validate",
            "system_status": "/api/v1/system/status",
            "recent_events": "/api/v1/memory/events",
            "events_by_type": "/api/v1/memory/events/{event_type}"
        },
        "capabilities": [
            "model_validation",
            "service_generation", 
            "test_execution",
            "deployment_automation",
            "performance_monitoring"
        ],
        "timestamp": datetime.now().isoformat()
    }

# Server information endpoint
@app.get("/api/v1/server/info", response_model=ServerInfoResponse, tags=["Server Info"])
async def get_server_info(authenticated: bool = Depends(verify_api_key)):
    """Get comprehensive server information and configuration"""
    try:
        # Check Legend Engine status
        engine_status = ServiceStatus(
            name="Legend Engine",
            url=os.getenv("LEGEND_ENGINE_URL", "http://localhost:6300"),
            status="configured",
            last_check=datetime.now().isoformat()
        )
        
        # Check Legend SDLC status  
        sdlc_status = ServiceStatus(
            name="Legend SDLC",
            url=os.getenv("LEGEND_SDLC_URL", "http://localhost:6100"),
            status="configured",
            last_check=datetime.now().isoformat()
        )
        
        # Get configuration summary
        config_summary = {
            "api_host": os.getenv("LEGEND_API_HOST", "0.0.0.0"),
            "api_port": os.getenv("LEGEND_API_PORT", "8000"),
            "debug_mode": os.getenv("LEGEND_API_DEBUG", "false"),
            "log_level": os.getenv("LEGEND_LOG_LEVEL", "INFO"),
            "api_keys_configured": bool(os.getenv("VALID_API_KEYS")),
            "legend_api_key_configured": bool(os.getenv("LEGEND_API_KEY"))
        }
        
        return ServerInfoResponse(
            service="Legend Guardian Agent API",
            version="1.0.0",
            description="API for monitoring and managing the FINOS Legend platform",
            environment="production" if not os.getenv("LEGEND_API_DEBUG", "false").lower() == "true" else "development",
            host=os.getenv("LEGEND_API_HOST", "0.0.0.0"),
            port=int(os.getenv("LEGEND_API_PORT", "8000")),
            debug_mode=os.getenv("LEGEND_API_DEBUG", "false").lower() == "true",
            timestamp=datetime.now().isoformat(),
            legend_services={
                "engine": engine_status,
                "sdlc": sdlc_status
            },
            api_endpoints={
                "health": "/health",
                "server_info": "/api/v1/server/info",
                "model_change": "/api/v1/model/change",
                "model_validation": "/api/v1/model/validate",
                "system_status": "/api/v1/system/status",
                "recent_events": "/api/v1/memory/events",
                "events_by_type": "/api/v1/memory/events/{event_type}"
            },
            configuration=config_summary,
            capabilities=[
                "model_validation",
                "service_generation",
                "test_execution", 
                "deployment_automation",
                "performance_monitoring"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error getting server info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get server info: {str(e)}"
        )
