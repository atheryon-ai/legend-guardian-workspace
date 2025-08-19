#!/usr/bin/env python3
"""
API Data Models

Pydantic models for API requests and responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelChangeRequest(BaseModel):
    """Request model for handling model changes"""

    event_type: str = Field(..., description="Type of model change event")
    model_id: str = Field(..., description="ID of the affected model")
    details: Dict[str, Any] = Field(
        ..., description="Additional details about the change"
    )


class ModelValidationRequest(BaseModel):
    """Request model for model validation"""

    model_id: str = Field(..., description="ID of the model to validate")


class SystemStatusResponse(BaseModel):
    """Response model for system status"""

    agent_status: str
    capabilities: List[str]
    memory_usage: Dict[str, int]
    last_activity: str


class ModelChangeResponse(BaseModel):
    """Response model for model change handling"""

    success: bool
    execution_time: int
    errors: List[str]
    output: Dict[str, Any]
    timestamp: str


class ServiceStatus(BaseModel):
    """Model for individual service status"""

    name: str
    url: str
    status: str
    response_time: Optional[float] = None
    last_check: str
    version: Optional[str] = None


class ServerInfoResponse(BaseModel):
    """Response model for server information"""

    service: str
    version: str
    description: str
    environment: str
    host: str
    port: int
    debug_mode: bool
    timestamp: str
    legend_services: Dict[str, ServiceStatus]
    api_endpoints: Dict[str, str]
    configuration: Dict[str, Any]
    capabilities: List[str]
