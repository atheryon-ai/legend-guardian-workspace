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
    SystemStatusResponse, ModelChangeResponse
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
    description="API for the Legend Guardian Agent - FINOS Legend platform monitoring and management",
    version="1.0.0",
    lifespan=lifespan
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
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Legend Guardian Agent API"
    }

# Model change handling endpoint
@app.post("/api/v1/model/change", response_model=ModelChangeResponse)
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
@app.post("/api/v1/model/validate")
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
@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
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
@app.get("/api/v1/memory/events")
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

@app.get("/api/v1/memory/events/{event_type}")
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
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Legend Guardian Agent API",
        "version": "1.0.0",
        "description": "API for monitoring and managing the FINOS Legend platform",
        "endpoints": {
            "health": "/health",
            "model_change": "/api/v1/model/change",
            "model_validation": "/api/v1/model/validate",
            "system_status": "/api/v1/system/status",
            "recent_events": "/api/v1/memory/events",
            "events_by_type": "/api/v1/memory/events/{event_type}"
        },
        "timestamp": datetime.now().isoformat()
    }
