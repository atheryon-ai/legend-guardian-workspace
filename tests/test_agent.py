#!/usr/bin/env python3
"""
Tests for the Legend Guardian Agent
"""

import pytest
from datetime import datetime
from src.agent.models import ModelChangeEvent, ChangeAnalysis, ActionPlan, ExecutionResult
from src.agent.memory import AgentMemory

def test_model_change_event():
    """Test ModelChangeEvent creation and serialization"""
    event = ModelChangeEvent(
        event_type="model_modification",
        model_id="Person",
        timestamp=datetime.now(),
        details={"field": "name", "change": "type modification"}
    )
    
    assert event.event_type == "model_modification"
    assert event.model_id == "Person"
    assert "field" in event.details
    assert event.to_dict()["event_type"] == "model_modification"

def test_change_analysis():
    """Test ChangeAnalysis creation and serialization"""
    event = ModelChangeEvent(
        event_type="model_modification",
        model_id="Person",
        timestamp=datetime.now(),
        details={}
    )
    
    analysis = ChangeAnalysis(
        event=event,
        impact_level="high",
        affected_services=["service_Person"],
        recommendations=["Run tests", "Update docs"]
    )
    
    assert analysis.impact_level == "high"
    assert len(analysis.affected_services) == 1
    assert len(analysis.recommendations) == 2
    assert analysis.to_dict()["impact_level"] == "high"

def test_action_plan():
    """Test ActionPlan creation and serialization"""
    event = ModelChangeEvent(
        event_type="model_modification",
        model_id="Person",
        timestamp=datetime.now(),
        details={}
    )
    
    analysis = ChangeAnalysis(
        event=event,
        impact_level="high",
        affected_services=["service_Person"],
        recommendations=[]
    )
    
    plan = ActionPlan(
        analysis=analysis,
        actions=["Validate model", "Run tests"],
        priority="high",
        estimated_duration=20
    )
    
    assert plan.priority == "high"
    assert plan.estimated_duration == 20
    assert len(plan.actions) == 2
    assert plan.to_dict()["priority"] == "high"

def test_agent_memory():
    """Test AgentMemory functionality"""
    memory = AgentMemory()
    
    # Create test data
    event = ModelChangeEvent(
        event_type="test",
        model_id="Test",
        timestamp=datetime.now(),
        details={}
    )
    
    analysis = ChangeAnalysis(
        event=event,
        impact_level="low",
        affected_services=[],
        recommendations=[]
    )
    
    plan = ActionPlan(
        analysis=analysis,
        actions=[],
        priority="low",
        estimated_duration=5
    )
    
    result = ExecutionResult(
        plan=plan,
        success=True,
        execution_time=1,
        errors=[],
        output={}
    )
    
    # Test storage
    memory.store(event, analysis, plan, result)
    
    assert len(memory.events) == 1
    assert len(memory.analyses) == 1
    assert len(memory.plans) == 1
    assert len(memory.results) == 1
    
    # Test retrieval
    recent_events = memory.get_recent_events(5)
    assert len(recent_events) == 1
    
    events_by_type = memory.get_events_by_type("test")
    assert len(events_by_type) == 1
