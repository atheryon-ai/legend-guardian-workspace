#!/usr/bin/env python3
"""
Agent Data Models

Data models for the Legend Guardian Agent system.
"""

from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AgentCapability(Enum):
    """Enumeration of Guardian Agent capabilities"""

    MODEL_VALIDATION = "model_validation"
    SERVICE_GENERATION = "service_generation"
    TEST_EXECUTION = "test_execution"
    DEPLOYMENT_AUTOMATION = "deployment_automation"
    PERFORMANCE_MONITORING = "performance_monitoring"


@dataclass
class ModelChangeEvent:
    """Represents a model change event in the Legend platform"""

    event_type: str
    model_id: str
    timestamp: datetime
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "model_id": self.model_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class ChangeAnalysis:
    """Analysis of a model change event"""

    event: ModelChangeEvent
    impact_level: str  # low, medium, high, critical
    affected_services: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event.to_dict(),
            "impact_level": self.impact_level,
            "affected_services": self.affected_services,
            "recommendations": self.recommendations,
        }


@dataclass
class ActionPlan:
    """Plan of actions to take based on change analysis"""

    analysis: ChangeAnalysis
    actions: List[str]
    priority: str  # low, medium, high, urgent
    estimated_duration: int  # in minutes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis": self.analysis.to_dict(),
            "actions": self.actions,
            "priority": self.priority,
            "estimated_duration": self.estimated_duration,
        }


@dataclass
class ExecutionResult:
    """Result of executing an action plan"""

    plan: ActionPlan
    success: bool
    execution_time: int  # in seconds
    errors: List[str]
    output: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan": self.plan.to_dict(),
            "success": self.success,
            "execution_time": self.execution_time,
            "errors": self.errors,
            "output": self.output,
        }
