#!/usr/bin/env python3
"""
Agent Memory System

Memory system for the Legend Guardian Agent.
"""

from typing import List
from .models import ModelChangeEvent, ChangeAnalysis, ActionPlan, ExecutionResult

class AgentMemory:
    """Memory system for the Guardian Agent"""
    
    def __init__(self):
        self.events: List[ModelChangeEvent] = []
        self.analyses: List[ChangeAnalysis] = []
        self.plans: List[ActionPlan] = []
        self.results: List[ExecutionResult] = []
    
    def store(self, event: ModelChangeEvent, analysis: ChangeAnalysis, plan: ActionPlan, result: ExecutionResult):
        """Store all components of an agent interaction"""
        self.events.append(event)
        self.analyses.append(analysis)
        self.plans.append(plan)
        self.results.append(result)
        
        # Keep only last 1000 interactions to prevent memory bloat
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
            self.analyses = self.analyses[-1000:]
            self.plans = self.plans[-1000:]
            self.results = self.results[-1000:]
    
    def get_recent_events(self, limit: int = 10) -> List[ModelChangeEvent]:
        """Get recent events"""
        return self.events[-limit:]
    
    def get_events_by_type(self, event_type: str) -> List[ModelChangeEvent]:
        """Get events filtered by type"""
        return [event for event in self.events if event.event_type == event_type]
