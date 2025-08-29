"""Agent orchestrator for planning and executing Legend operations."""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
import yaml

from src.agent.memory import MemoryStore
from src.agent.policies import PolicyEngine
from src.clients.depot import DepotClient
from src.clients.engine import EngineClient
from src.clients.sdlc import SDLCClient
from src.settings import Settings

logger = structlog.get_logger()


class AgentOrchestrator:
    """Orchestrates agent operations across Legend services."""
    
    def __init__(self, settings: Settings):
        """Initialize orchestrator."""
        self.settings = settings
        self.engine_client = EngineClient(settings)
        self.sdlc_client = SDLCClient(settings)
        self.depot_client = DepotClient(settings)
        self.memory = MemoryStore()
        self.policy_engine = PolicyEngine()
    
    async def parse_intent(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse natural language intent into execution plan.
        
        Args:
            prompt: Natural language prompt
            context: Optional context
        
        Returns:
            List of planned steps
        """
        logger.info("Parsing intent", prompt=prompt[:100])
        
        # Simple rule-based parsing for demonstration
        # In production, this would use LLM or NLP
        steps = []
        prompt_lower = prompt.lower()
        
        if "create" in prompt_lower and "model" in prompt_lower:
            steps.append({
                "action": "create_model",
                "params": self._extract_model_params(prompt),
            })
        
        if "compile" in prompt_lower:
            steps.append({
                "action": "compile",
                "params": {},
            })
        
        if "generate" in prompt_lower and "service" in prompt_lower:
            steps.append({
                "action": "generate_service",
                "params": self._extract_service_params(prompt),
            })
        
        if "open" in prompt_lower and ("pr" in prompt_lower or "review" in prompt_lower):
            steps.append({
                "action": "open_review",
                "params": {"title": "Changes from agent"},
            })
        
        if "publish" in prompt_lower:
            steps.append({
                "action": "publish",
                "params": {},
            })
        
        # Apply policies to plan
        steps = await self.policy_engine.validate_plan(steps)
        
        # Store in memory
        self.memory.add_episode({
            "id": str(uuid.uuid4()),
            "prompt": prompt,
            "plan": steps,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return steps
    
    async def execute_step(
        self,
        action: str,
        params: Dict[str, Any],
    ) -> Any:
        """
        Execute a single step.
        
        Args:
            action: Action to execute
            params: Action parameters
        
        Returns:
            Execution result
        """
        logger.info("Executing step", action=action, params=params)
        
        # Route to appropriate handler
        handlers = {
            "create_workspace": self._create_workspace,
            "create_model": self._create_model,
            "create_mapping": self._create_mapping,
            "compile": self._compile,
            "generate_service": self._generate_service,
            "open_review": self._open_review,
            "search_depot": self._search_depot,
            "import_model": self._import_model,
            "transform_schema": self._transform_schema,
            "run_tests": self._run_tests,
            "publish": self._publish,
        }
        
        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        # Apply pre-execution policies
        await self.policy_engine.check_action(action, params)
        
        # Execute
        result = await handler(params)
        
        # Store result in memory
        self.memory.add_action({
            "action": action,
            "params": params,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return result
    
    async def validate_step(
        self,
        action: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate a step without executing.
        
        Args:
            action: Action to validate
            params: Action parameters
        
        Returns:
            Validation result
        """
        try:
            await self.policy_engine.check_action(action, params)
            return {"valid": True, "issues": []}
        except Exception as e:
            return {"valid": False, "issues": [str(e)]}
    
    # Handler methods
    
    async def _create_workspace(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workspace."""
        return await self.sdlc_client.create_workspace(
            project_id=params["project_id"],
            workspace_id=params["workspace_id"],
        )
    
    async def _create_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a model from CSV or specification."""
        model_name = params.get("name", "GeneratedModel")
        csv_data = params.get("csv_data", "")
        
        # Generate PURE model from CSV structure
        pure_model = self._generate_pure_from_csv(model_name, csv_data)
        
        # Upsert to workspace
        entities = [{
            "path": f"model::{model_name}",
            "classifierPath": "meta::pure::metamodel::type::Class",
            "content": {
                "name": model_name,
                "package": "model",
                "properties": self._extract_properties_from_csv(csv_data),
            },
        }]
        
        await self.sdlc_client.upsert_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            entities=entities,
        )
        
        return {"model": model_name, "pure": pure_model}
    
    async def _create_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mapping."""
        mapping_name = params.get("name", "GeneratedMapping")
        model = params.get("model", "Model")
        
        # Generate mapping
        mapping = {
            "path": f"mapping::{mapping_name}",
            "classifierPath": "meta::pure::mapping::Mapping",
            "content": {
                "name": mapping_name,
                "package": "mapping",
                "classMappings": [],
            },
        }
        
        await self.sdlc_client.upsert_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            entities=[mapping],
        )
        
        return {"mapping": mapping_name}
    
    async def _compile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compile current workspace."""
        # Get all entities
        entities = await self.sdlc_client.get_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
        )
        
        # Convert to PURE
        pure = self._entities_to_pure(entities)
        
        # Compile
        result = await self.engine_client.compile(pure)
        
        return result
    
    async def _generate_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a service."""
        path = params.get("path", "generated/service")
        
        # Generate service specification
        service = {
            "path": f"service::{path.replace('/', '::')}",
            "classifierPath": "meta::legend::service::Service",
            "content": {
                "pattern": f"/api/service/{path}",
                "documentation": "Generated service",
                "execution": {},
            },
        }
        
        await self.sdlc_client.upsert_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            entities=[service],
        )
        
        return {"service_path": path}
    
    async def _open_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Open a review/PR."""
        title = params.get("title", "Agent-generated changes")
        description = params.get("description", "Changes generated by Legend Guardian Agent")
        
        review = await self.sdlc_client.create_review(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            title=title,
            description=description,
        )
        
        return review
    
    async def _search_depot(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search depot for models."""
        query = params.get("query", "")
        return await self.depot_client.search(query)
    
    async def _import_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import model from depot."""
        # Implementation would fetch from depot and add to workspace
        return {"imported": True}
    
    async def _transform_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transform model to schema format."""
        format_type = params.get("format", "avro")
        class_path = params.get("class_path", "model::Model")
        
        schema = await self.engine_client.transform_to_schema(
            schema_type=format_type,
            class_path=class_path,
        )
        
        return {"schema": schema, "format": format_type}
    
    async def _run_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run tests."""
        results = await self.engine_client.run_tests()
        passed = all(r["passed"] for r in results)
        
        return {"passed": passed, "results": results}
    
    async def _publish(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish to depot."""
        version = params.get("version", "1.0.0")
        
        result = await self.depot_client.publish(
            project_id=self.settings.project_id,
            version=version,
        )
        
        return result
    
    # Helper methods
    
    def _extract_model_params(self, prompt: str) -> Dict[str, Any]:
        """Extract model parameters from prompt."""
        # Simple extraction logic
        params = {"name": "Model"}
        
        if "trade" in prompt.lower():
            params["name"] = "Trade"
        elif "position" in prompt.lower():
            params["name"] = "Position"
        
        return params
    
    def _extract_service_params(self, prompt: str) -> Dict[str, Any]:
        """Extract service parameters from prompt."""
        params = {"path": "service/generated"}
        
        if "byNotional" in prompt:
            params["path"] = "trades/byNotional"
        elif "byTicker" in prompt:
            params["path"] = "trades/byTicker"
        
        return params
    
    def _generate_pure_from_csv(self, model_name: str, csv_data: str) -> str:
        """Generate PURE model from CSV."""
        # Simple CSV to PURE conversion
        lines = csv_data.strip().split("\n")
        if not lines:
            return f"Class {model_name} {{}}"
        
        headers = lines[0].split(",") if lines else []
        
        properties = []
        for header in headers:
            prop_name = header.strip()
            properties.append(f"  {prop_name}: String[1];")
        
        pure = f"""Class model::{model_name}
{{
{chr(10).join(properties)}
}}"""
        
        return pure
    
    def _extract_properties_from_csv(self, csv_data: str) -> List[Dict[str, Any]]:
        """Extract properties from CSV."""
        lines = csv_data.strip().split("\n")
        if not lines:
            return []
        
        headers = lines[0].split(",") if lines else []
        
        properties = []
        for header in headers:
            prop_name = header.strip()
            properties.append({
                "name": prop_name,
                "type": "String",
                "multiplicity": {"lowerBound": 1, "upperBound": 1},
            })
        
        return properties
    
    def _entities_to_pure(self, entities: List[Dict[str, Any]]) -> str:
        """Convert entities to PURE code."""
        pure_parts = []
        
        for entity in entities:
            classifier = entity.get("classifierPath", "")
            content = entity.get("content", {})
            
            if "Class" in classifier:
                pure_parts.append(self._class_to_pure(content))
            elif "Mapping" in classifier:
                pure_parts.append(self._mapping_to_pure(content))
            # Add more conversions as needed
        
        return "\n\n".join(pure_parts)
    
    def _class_to_pure(self, content: Dict[str, Any]) -> str:
        """Convert class to PURE."""
        name = content.get("name", "UnknownClass")
        package = content.get("package", "model")
        properties = content.get("properties", [])
        
        prop_lines = []
        for prop in properties:
            prop_name = prop.get("name")
            prop_type = prop.get("type", "String")
            mult = prop.get("multiplicity", {})
            lower = mult.get("lowerBound", 1)
            upper = mult.get("upperBound", 1)
            
            mult_str = f"[{lower}..{upper}]" if upper != "*" else f"[{lower}..*]"
            prop_lines.append(f"  {prop_name}: {prop_type}{mult_str};")
        
        return f"""Class {package}::{name}
{{
{chr(10).join(prop_lines)}
}}"""
    
    def _mapping_to_pure(self, content: Dict[str, Any]) -> str:
        """Convert mapping to PURE."""
        name = content.get("name", "UnknownMapping")
        package = content.get("package", "mapping")
        
        return f"""Mapping {package}::{name}
(
  // Mapping implementation
)"""