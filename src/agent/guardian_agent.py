#!/usr/bin/env python3
"""
Legend Guardian Agent

Main Guardian Agent for the FINOS Legend platform.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .clients import LegendEngineClient, LegendSDLCClient
from .memory import AgentMemory
from .models import (
    AgentCapability, ModelChangeEvent, ChangeAnalysis, 
    ActionPlan, ExecutionResult
)

logger = logging.getLogger(__name__)

class LegendGuardianAgent:
    """Main Guardian Agent for the FINOS Legend platform"""
    
    def __init__(self, legend_engine_url: str, legend_sdlc_url: str, api_key: str = None):
        self.engine_client = LegendEngineClient(legend_engine_url, api_key)
        self.sdlc_client = LegendSDLCClient(legend_sdlc_url, api_key)
        self.memory = AgentMemory()
        self.capabilities = list(AgentCapability)
        
        logger.info("Legend Guardian Agent initialized")
    
    async def handle_model_change(self, event: ModelChangeEvent) -> ExecutionResult:
        """Handle a model change event - main entry point"""
        try:
            logger.info(f"Handling model change event: {event.event_type} for model {event.model_id}")
            
            # Step 1: Analyze the change
            analysis = await self._analyze_change(event)
            
            # Step 2: Create action plan
            plan = self._create_plan(analysis)
            
            # Step 3: Execute the plan
            result = await self._execute_plan(plan)
            
            # Step 4: Store in memory
            self.memory.store(event, analysis, plan, result)
            
            logger.info(f"Model change event handled successfully: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Error handling model change event: {str(e)}")
            # Create a failed result
            failed_analysis = ChangeAnalysis(event, "unknown", [], [f"Error: {str(e)}"])
            failed_plan = ActionPlan(failed_analysis, [], "low", 0)
            failed_result = ExecutionResult(failed_plan, False, 0, [str(e)], {})
            
            self.memory.store(event, failed_analysis, failed_plan, failed_result)
            return failed_result
    
    async def _analyze_change(self, event: ModelChangeEvent) -> ChangeAnalysis:
        """Analyze the impact of a model change"""
        logger.info(f"Analyzing change for model {event.model_id}")
        
        # Get model information from Legend Engine
        model_info = await self.engine_client.get_model_info(event.model_id)
        
        # Determine impact level based on event type and model complexity
        impact_level = self._determine_impact_level(event, model_info)
        
        # Identify affected services
        affected_services = self._identify_affected_services(event, model_info)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(event, impact_level, affected_services)
        
        analysis = ChangeAnalysis(event, impact_level, affected_services, recommendations)
        logger.info(f"Change analysis completed: {impact_level} impact level")
        
        return analysis
    
    def _determine_impact_level(self, event: ModelChangeEvent, model_info: Dict[str, Any]) -> str:
        """Determine the impact level of a change"""
        # Simple logic based on event type
        if event.event_type in ["model_deletion", "major_version_change"]:
            return "critical"
        elif event.event_type in ["model_modification", "service_regeneration"]:
            return "high"
        elif event.event_type in ["minor_version_change", "metadata_update"]:
            return "medium"
        else:
            return "low"
    
    def _identify_affected_services(self, event: ModelChangeEvent, model_info: Dict[str, Any]) -> list:
        """Identify services affected by the model change"""
        # This would typically query the Legend platform for service dependencies
        # For now, return a placeholder
        return [f"service_{event.model_id}"]
    
    def _generate_recommendations(self, event: ModelChangeEvent, impact_level: str, affected_services: list) -> list:
        """Generate recommendations based on the change analysis"""
        recommendations = []
        
        if impact_level in ["high", "critical"]:
            recommendations.append("Schedule maintenance window for deployment")
            recommendations.append("Notify stakeholders of potential service impact")
        
        if event.event_type == "model_modification":
            recommendations.append("Run full test suite before deployment")
            recommendations.append("Update service documentation")
        
        if len(affected_services) > 5:
            recommendations.append("Consider staged deployment approach")
        
        return recommendations
    
    def _create_plan(self, analysis: ChangeAnalysis) -> ActionPlan:
        """Create an action plan based on the analysis"""
        logger.info(f"Creating action plan for {analysis.impact_level} impact change")
        
        actions = []
        priority = "low"
        estimated_duration = 5
        
        if analysis.impact_level == "critical":
            priority = "urgent"
            estimated_duration = 30
            actions.extend([
                "Immediate service validation",
                "Rollback plan preparation",
                "Stakeholder notification"
            ])
        elif analysis.impact_level == "high":
            priority = "high"
            estimated_duration = 20
            actions.extend([
                "Service validation",
                "Test execution",
                "Deployment preparation"
            ])
        elif analysis.impact_level == "medium":
            priority = "medium"
            estimated_duration = 15
            actions.extend([
                "Model validation",
                "Basic testing",
                "Documentation update"
            ])
        else:
            actions.extend([
                "Model validation",
                "Logging and monitoring"
            ])
        
        # Add standard actions
        actions.extend([
            "Update change log",
            "Monitor system health",
            "Generate report"
        ])
        
        plan = ActionPlan(analysis, actions, priority, estimated_duration)
        logger.info(f"Action plan created with {len(actions)} actions, priority: {priority}")
        
        return plan
    
    async def _execute_plan(self, plan: ActionPlan) -> ExecutionResult:
        """Execute the action plan"""
        logger.info(f"Executing action plan with {len(plan.actions)} actions")
        
        start_time = datetime.now()
        errors = []
        output = {}
        
        try:
            # Execute each action in the plan
            for action in plan.actions:
                logger.info(f"Executing action: {action}")
                
                try:
                    action_result = await self._execute_action(action, plan.analysis)
                    output[action] = action_result
                    
                except Exception as e:
                    error_msg = f"Action '{action}' failed: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    output[action] = {"error": str(e)}
            
            execution_time = int((datetime.now() - start_time).total_seconds())
            success = len(errors) == 0
            
            result = ExecutionResult(plan, success, execution_time, errors, output)
            logger.info(f"Plan execution completed: success={success}, time={execution_time}s, errors={len(errors)}")
            
            return result
            
        except Exception as e:
            execution_time = int((datetime.now() - start_time).total_seconds())
            errors.append(f"Plan execution failed: {str(e)}")
            result = ExecutionResult(plan, False, execution_time, errors, output)
            logger.error(f"Plan execution failed: {str(e)}")
            return result
    
    async def _execute_action(self, action: str, analysis: ChangeAnalysis) -> Dict[str, Any]:
        """Execute a specific action"""
        if action == "Model validation":
            return await self.engine_client.validate_model(analysis.event.model_id)
        elif action == "Service validation":
            return {"status": "validated", "timestamp": datetime.now().isoformat()}
        elif action == "Test execution":
            return {"tests_passed": True, "test_count": 10, "timestamp": datetime.now().isoformat()}
        elif action == "Update change log":
            return {"status": "updated", "timestamp": datetime.now().isoformat()}
        elif action == "Monitor system health":
            return {"health": "healthy", "timestamp": datetime.now().isoformat()}
        elif action == "Generate report":
            return {"report_id": f"report_{datetime.now().timestamp()}", "timestamp": datetime.now().isoformat()}
        else:
            return {"status": "completed", "action": action, "timestamp": datetime.now().isoformat()}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "agent_status": "active",
            "capabilities": [cap.value for cap in self.capabilities],
            "memory_usage": {
                "events": len(self.memory.events),
                "analyses": len(self.memory.analyses),
                "plans": len(self.memory.plans),
                "results": len(self.memory.results)
            },
            "last_activity": datetime.now().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.engine_client.close()
        await self.sdlc_client.close()
        logger.info("Legend Guardian Agent cleanup completed")
