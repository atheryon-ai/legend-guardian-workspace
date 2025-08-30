"""Agent orchestrator for planning and executing Legend operations."""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
import yaml

from legend_guardian.agent.memory import MemoryStore
from legend_guardian.agent.policies import PolicyEngine
from legend_guardian.agent.llm_client import LLMClient
from legend_guardian.rag.store import VectorStore
from legend_guardian.clients.depot import DepotClient
from legend_guardian.clients.engine import EngineClient
from legend_guardian.clients.sdlc import SDLCClient
from legend_guardian.config import Settings

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
        
        # Initialize LLM client if configured
        llm_provider = settings.agent_model.split("-")[0] if "-" in settings.agent_model else "openai"
        self.llm_client = LLMClient(provider=llm_provider, model=settings.agent_model)
    
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
        
        # Try LLM-based parsing first, fall back to rule-based
        try:
            steps = await self.llm_client.parse_intent(prompt, context)
            if steps:
                logger.info(f"LLM parsed {len(steps)} steps from intent")
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
        except Exception as e:
            logger.warning(f"LLM parsing failed, using rule-based: {e}")
        
        # Fallback to rule-based parsing
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
            # Phase 2: Model Management
            "apply_changes": self._apply_changes,
            "create_v2_service": self._create_v2_service,
            "create_service": self._create_service,
            # Phase 3: Data Operations
            "analyze_table": self._analyze_table,
            "generate_model": self._generate_model,
            "add_constraints": self._add_constraints,
            "plan_ingestion": self._plan_ingestion,
            "execute_backfill": self._execute_backfill,
            "validate_sample": self._validate_sample,
            "record_manifest": self._record_manifest,
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
        project_id = params.get("project_id", self.settings.project_id)
        workspace_id = params.get("workspace_id", self.settings.workspace_id)
        depot_project_id = params.get("depot_project_id")
        version = params.get("version", "latest")
        entity_paths = params.get("entity_paths", [])  # Specific entities to import
        
        try:
            # Get the latest version if not specified
            if version == "latest":
                version = await self.depot_client.get_latest_version(depot_project_id)
                logger.info(f"Using latest version: {version}")
            
            # Get entities from depot
            entities = await self.depot_client.get_entities(
                project_id=depot_project_id,
                version=version
            )
            
            # Filter entities if specific paths requested
            if entity_paths:
                entities = [e for e in entities if e.get("path") in entity_paths]
            
            # Transform depot entities to SDLC format
            sdlc_entities = []
            for entity in entities:
                sdlc_entity = {
                    "path": entity.get("path"),
                    "classifierPath": entity.get("classifierPath"),
                    "content": entity.get("content")
                }
                sdlc_entities.append(sdlc_entity)
            
            # Import to workspace
            if sdlc_entities:
                await self.sdlc_client.upsert_entities(
                    project_id=project_id,
                    workspace_id=workspace_id,
                    entities=sdlc_entities,
                    replace=False  # Merge, don't replace existing
                )
                
                logger.info(f"Imported {len(sdlc_entities)} entities from depot")
                
                return {
                    "imported": True,
                    "count": len(sdlc_entities),
                    "depot_project": depot_project_id,
                    "version": version,
                    "entities": [e["path"] for e in sdlc_entities]
                }
            else:
                logger.warning("No entities found to import")
                return {
                    "imported": False,
                    "message": "No entities found matching criteria"
                }
                
        except Exception as e:
            logger.error(f"Failed to import from depot: {e}")
            return {
                "imported": False,
                "error": str(e)
            }
    
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
    
    # Phase 1: Core Compilation & Service Generation
    
    async def _compile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile PURE code in workspace.
        
        Args:
            params: Optional project_id and workspace_id
        
        Returns:
            Compilation result with status and errors
        """
        project_id = params.get("project_id", self.settings.project_id)
        workspace_id = params.get("workspace_id", self.settings.workspace_id)
        
        logger.info(f"Compiling workspace: {project_id}/{workspace_id}")
        
        try:
            # Step 1: Get entities from workspace
            entities = await self.sdlc_client.get_entities(
                project_id=project_id,
                workspace_id=workspace_id,
            )
            
            if not entities:
                return {
                    "status": "error",
                    "errors": [{"message": "No entities found in workspace"}],
                }
            
            # Step 2: Convert entities to PURE code
            pure_code = self._entities_to_pure(entities)
            
            if not pure_code:
                return {
                    "status": "error",
                    "errors": [{"message": "Failed to convert entities to PURE"}],
                }
            
            # Step 3: Compile PURE code
            result = await self.engine_client.compile(
                pure=pure_code,
                project_id=project_id,
                workspace_id=workspace_id,
            )
            
            # Return standardized result
            return {
                "status": "success" if result.get("status") == "success" else "failed",
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
                "entity_count": len(entities),
                "pure_size": len(pure_code),
            }
            
        except Exception as e:
            logger.error(f"Compilation failed: {e}")
            return {
                "status": "error",
                "errors": [{"message": str(e)}],
            }
    
    async def _generate_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate service definition in workspace.
        
        Note: Services are not dynamically generated via API.
        This creates a service definition that will be built when merged.
        
        Args:
            params: Service path, query, mapping, runtime
        
        Returns:
            Service definition creation result
        """
        service_path = params.get("path", "generated/service")
        query = params.get("query", "")
        mapping = params.get("mapping", "")
        runtime = params.get("runtime", "")
        
        logger.info(f"Creating service definition: {service_path}")
        
        # Convert path to valid service name
        service_name = service_path.replace("/", "_").replace("-", "_")
        
        # Create service definition entity
        service_entity = {
            "path": f"service::{service_name}",
            "classifierPath": "meta::legend::service::metamodel::Service",
            "content": {
                "name": service_name,
                "pattern": f"/{service_path}",
                "owners": ["guardian-agent"],
                "documentation": f"Service generated by Legend Guardian Agent",
                "execution": {
                    "single": {
                        "query": query or f"model::all{service_name}",
                        "mapping": mapping or f"mapping::{service_name}Mapping",
                        "runtime": runtime or f"runtime::{service_name}Runtime",
                    }
                },
            },
        }
        
        try:
            # Add service definition to workspace
            result = await self.sdlc_client.upsert_entities(
                project_id=self.settings.project_id,
                workspace_id=self.settings.workspace_id,
                entities=[service_entity],
            )
            
            return {
                "service_path": service_path,
                "service_name": service_name,
                "status": "defined",
                "url": f"{self.settings.engine_url}/api/service/{service_path}",
                "note": "Service defined. Merge to master and run build pipeline to deploy.",
            }
            
        except Exception as e:
            logger.error(f"Service generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def _open_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Open merge request/pull request for workspace changes.
        
        Args:
            params: Review title and description
        
        Returns:
            Review creation result
        """
        title = params.get("title", "Agent-generated changes")
        description = params.get("description", "Changes created by Legend Guardian Agent")
        project_id = params.get("project_id", self.settings.project_id)
        workspace_id = params.get("workspace_id", self.settings.workspace_id)
        
        logger.info(f"Creating review for workspace: {workspace_id}")
        
        try:
            # Create review using SDLC client
            result = await self.sdlc_client.create_review(
                project_id=project_id,
                workspace_id=workspace_id,
                title=title,
                description=description,
            )
            
            return {
                "review_id": result.get("id", "unknown"),
                "url": result.get("web_url", ""),
                "state": result.get("state", "opened"),
                "workspace": workspace_id,
            }
            
        except Exception as e:
            logger.error(f"Review creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "note": "Review creation requires GitLab integration setup",
            }
    
    async def _create_mapping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a mapping between source and target.
        
        Args:
            params: Mapping name, source, target
        
        Returns:
            Mapping creation result
        """
        mapping_name = params.get("name", "GeneratedMapping")
        model_name = params.get("model", "Model")
        source = params.get("source", "FlatData")
        
        logger.info(f"Creating mapping: {mapping_name}")
        
        # Create basic mapping entity
        mapping_entity = {
            "path": f"mapping::{mapping_name}",
            "classifierPath": "meta::pure::mapping::Mapping",
            "content": {
                "name": mapping_name,
                "package": "mapping",
                "classMappings": [
                    {
                        "class": f"model::{model_name}",
                        "root": True,
                        "mappings": [
                            # Property mappings would be generated based on model
                            # This is a simplified version
                        ],
                    }
                ],
            },
        }
        
        try:
            # Add mapping to workspace
            result = await self.sdlc_client.upsert_entities(
                project_id=self.settings.project_id,
                workspace_id=self.settings.workspace_id,
                entities=[mapping_entity],
            )
            
            return {
                "mapping": mapping_name,
                "status": "created",
                "model": model_name,
            }
            
        except Exception as e:
            logger.error(f"Mapping creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    # Phase 2: Model Management
    
    async def _apply_changes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply changes to a model (rename fields, add fields, etc.).
        
        Args:
            params: Model path and changes to apply
        
        Returns:
            Change application result
        """
        model_path = params.get("model_path", "")
        changes = params.get("changes", {})
        
        logger.info(f"Applying changes to model: {model_path}")
        
        try:
            # Get current model
            entities = await self.sdlc_client.get_entities(
                project_id=self.settings.project_id,
                workspace_id=self.settings.workspace_id,
            )
            
            # Find target model
            model_entity = None
            for entity in entities:
                if entity.get("path") == model_path:
                    model_entity = entity
                    break
            
            if not model_entity:
                return {"status": "error", "error": f"Model {model_path} not found"}
            
            # Apply changes
            content = model_entity.get("content", {})
            properties = content.get("properties", [])
            
            # Handle rename operations
            if "rename" in changes:
                for old_name, new_name in changes["rename"].items():
                    for prop in properties:
                        if prop.get("name") == old_name:
                            prop["name"] = new_name
            
            # Handle add field operations
            if "add_field" in changes:
                field = changes["add_field"]
                properties.append({
                    "name": field.get("name", "newField"),
                    "type": field.get("type", "String"),
                    "multiplicity": {
                        "lowerBound": 0,
                        "upperBound": 1,
                    },
                })
            
            content["properties"] = properties
            model_entity["content"] = content
            
            # Update model
            await self.sdlc_client.upsert_entities(
                project_id=self.settings.project_id,
                workspace_id=self.settings.workspace_id,
                entities=[model_entity],
            )
            
            return {
                "status": "success",
                "changes_applied": len(changes),
                "model_path": model_path,
            }
            
        except Exception as e:
            logger.error(f"Apply changes failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _create_v2_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a versioned service (v2) while keeping v1.
        
        Args:
            params: Service configuration and keep_v1 flag
        
        Returns:
            V2 service creation result
        """
        keep_v1 = params.get("keep_v1", True)
        base_path = params.get("base_path", "service")
        
        logger.info(f"Creating v2 service, keep_v1={keep_v1}")
        
        # Create v2 service path
        v2_path = f"{base_path}/v2"
        
        # Generate v2 service
        result = await self._generate_service({
            "path": v2_path,
            "query": params.get("query"),
            "mapping": params.get("mapping"),
            "runtime": params.get("runtime"),
        })
        
        result["v2_path"] = v2_path
        result["v1_maintained"] = keep_v1
        
        return result
    
    async def _create_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a service from imported model.
        
        Args:
            params: Service name and configuration
        
        Returns:
            Service creation result
        """
        service_name = params.get("name", "ImportedService")
        
        logger.info(f"Creating service: {service_name}")
        
        # Delegate to generate_service with appropriate params
        return await self._generate_service({
            "path": f"services/{service_name}",
            "query": params.get("query", f"model::all{service_name}"),
            "mapping": params.get("mapping", f"mapping::{service_name}Mapping"),
            "runtime": params.get("runtime", f"runtime::{service_name}Runtime"),
        })
    
    # Phase 3: Data Operations Handlers
    
    async def _analyze_table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze database table structure for reverse ETL.
        
        Args:
            params: Contains 'table' name and optional 'connection' details
        
        Returns:
            Table schema information
        """
        table_name = params.get("table", "")
        connection = params.get("connection", {})
        
        logger.info(f"Analyzing table: {table_name}")
        
        # For now, simulate table analysis with common patterns
        # In production, this would connect to actual database
        schema_info = self._simulate_table_analysis(table_name)
        
        # If using LLM, enhance with intelligent type inference
        if self.llm_client:
            try:
                enhanced_schema = await self.llm_client.enhance_schema(
                    table_name=table_name,
                    raw_schema=schema_info
                )
                if enhanced_schema:
                    schema_info = enhanced_schema
            except Exception as e:
                logger.warning(f"LLM schema enhancement failed: {e}")
        
        return {
            "table": table_name,
            "columns": schema_info.get("columns", []),
            "row_count": schema_info.get("row_count", 0),
            "primary_key": schema_info.get("primary_key"),
            "foreign_keys": schema_info.get("foreign_keys", []),
            "indexes": schema_info.get("indexes", []),
        }
    
    async def _generate_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate PURE model from database analysis.
        
        Args:
            params: Model name and schema information
        
        Returns:
            Generated model details
        """
        model_name = params.get("name", "GeneratedModel")
        schema = params.get("schema", {})
        columns = schema.get("columns", [])
        
        logger.info(f"Generating model: {model_name} from schema")
        
        # Generate PURE code from schema
        pure_code = self._generate_pure_from_schema(
            model_name=model_name,
            columns=columns,
            constraints=params.get("constraints", [])
        )
        
        # Create the model in SDLC
        entities = [{
            "path": f"model::{model_name}",
            "classifierPath": "meta::pure::metamodel::type::Class",
            "content": {
                "name": model_name,
                "package": "model",
                "properties": self._columns_to_properties(columns),
                "constraints": params.get("constraints", []),
            }
        }]
        
        result = await self.sdlc_client.upsert_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            entities=entities,
        )
        
        return {
            "model": model_name,
            "pure": pure_code,
            "properties_count": len(columns),
            "constraints_added": len(params.get("constraints", [])),
        }
    
    async def _add_constraints(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add constraints to a model.
        
        Args:
            params: Model path and constraints to add
        
        Returns:
            Result of adding constraints
        """
        model_path = params.get("model_path", "")
        constraints = params.get("constraints", [])
        
        logger.info(f"Adding {len(constraints)} constraints to {model_path}")
        
        # Get current model from SDLC
        entities = await self.sdlc_client.get_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
        )
        
        # Find the target model
        model_entity = None
        for entity in entities:
            if entity.get("path") == model_path:
                model_entity = entity
                break
        
        if not model_entity:
            raise ValueError(f"Model {model_path} not found")
        
        # Add constraints to model content
        content = model_entity.get("content", {})
        existing_constraints = content.get("constraints", [])
        
        # Convert string constraint names to constraint objects
        new_constraints = []
        for constraint in constraints:
            if isinstance(constraint, str):
                # Map common constraint names to PURE expressions
                if constraint == "qtyPositive":
                    new_constraints.append({
                        "name": "qtyPositive",
                        "functionDefinition": {
                            "body": "$this.quantity > 0"
                        }
                    })
                elif constraint == "validTicker":
                    new_constraints.append({
                        "name": "validTicker",
                        "functionDefinition": {
                            "body": "$this.ticker->isNotEmpty()"
                        }
                    })
                elif constraint == "notNull":
                    new_constraints.append({
                        "name": "notNull",
                        "functionDefinition": {
                            "body": "$this->isNotEmpty()"
                        }
                    })
                else:
                    # Generic constraint
                    new_constraints.append({
                        "name": constraint,
                        "functionDefinition": {
                            "body": f"// TODO: Implement {constraint}"
                        }
                    })
            else:
                new_constraints.append(constraint)
        
        # Merge constraints
        content["constraints"] = existing_constraints + new_constraints
        model_entity["content"] = content
        
        # Update the model
        result = await self.sdlc_client.upsert_entities(
            project_id=self.settings.project_id,
            workspace_id=self.settings.workspace_id,
            entities=[model_entity],
        )
        
        return {
            "model_path": model_path,
            "constraints_added": len(new_constraints),
            "total_constraints": len(content["constraints"]),
        }
    
    async def _plan_ingestion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan bulk data ingestion strategy.
        
        Args:
            params: Data source, window size, processing strategy
        
        Returns:
            Ingestion plan with windows and estimated time
        """
        data_source = params.get("source", "")
        window_size = params.get("window_size", 1000)
        parallel_windows = params.get("parallel_windows", 4)
        
        logger.info(f"Planning ingestion from: {data_source}")
        
        # Analyze data source to determine size
        source_info = await self._analyze_data_source(data_source)
        total_records = source_info.get("total_records", 0)
        
        # Calculate windows
        num_windows = (total_records + window_size - 1) // window_size
        
        # Create execution plan
        windows = []
        for i in range(num_windows):
            start_offset = i * window_size
            end_offset = min((i + 1) * window_size, total_records)
            
            windows.append({
                "window_id": i,
                "start_offset": start_offset,
                "end_offset": end_offset,
                "record_count": end_offset - start_offset,
                "status": "pending",
            })
        
        # Estimate processing time
        records_per_second = 100  # Conservative estimate
        estimated_seconds = total_records / records_per_second / parallel_windows
        
        return {
            "total_records": total_records,
            "window_size": window_size,
            "windows": len(windows),
            "parallel_windows": parallel_windows,
            "estimated_duration_seconds": estimated_seconds,
            "execution_plan": windows[:5],  # Return first 5 windows as sample
        }
    
    async def _execute_backfill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute bulk data backfill operation.
        
        Args:
            params: Target model, execution plan, validation rules
        
        Returns:
            Backfill execution results
        """
        target_model = params.get("target", "")
        execution_plan = params.get("execution_plan", [])
        validate = params.get("validate", True)
        
        logger.info(f"Executing backfill to model: {target_model}")
        
        # Track execution metrics
        processed = 0
        failed = 0
        start_time = datetime.utcnow()
        errors = []
        
        # Process windows (simulated)
        for window in execution_plan:
            try:
                # In production, this would process actual data
                window_result = await self._process_window(
                    window=window,
                    target_model=target_model,
                    validate=validate
                )
                
                processed += window_result.get("processed", 0)
                failed += window_result.get("failed", 0)
                
                if window_result.get("errors"):
                    errors.extend(window_result["errors"][:5])  # Keep first 5 errors per window
                    
            except Exception as e:
                logger.error(f"Window {window.get('window_id')} failed: {e}")
                failed += window.get("record_count", 0)
                errors.append(str(e))
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        success_rate = (processed / (processed + failed) * 100) if (processed + failed) > 0 else 0
        
        return {
            "processed": processed,
            "failed": failed,
            "success_rate": f"{success_rate:.2f}%",
            "duration_seconds": duration,
            "errors": errors[:10],  # Return first 10 errors
            "target_model": target_model,
            "completed_at": end_time.isoformat(),
        }
    
    async def _validate_sample(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a sample of data before full backfill.
        
        Args:
            params: Sample size, validation rules
        
        Returns:
            Validation results
        """
        sample_size = params.get("size", 100)
        validation_rules = params.get("rules", [])
        
        logger.info(f"Validating sample of {sample_size} records")
        
        # Simulate sample validation
        validation_results = {
            "sample_size": sample_size,
            "valid_records": sample_size - 5,  # Assume 5 invalid
            "invalid_records": 5,
            "validation_errors": [],
            "sample_valid": True,
        }
        
        # Apply validation rules
        for rule in validation_rules:
            rule_result = self._apply_validation_rule(rule, sample_size)
            if not rule_result["passed"]:
                validation_results["validation_errors"].append(rule_result)
                validation_results["sample_valid"] = False
        
        # Calculate validation score
        validation_results["validation_score"] = (
            validation_results["valid_records"] / sample_size * 100
        )
        
        return validation_results
    
    async def _record_manifest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record manifest of bulk operation for audit.
        
        Args:
            params: Operation details, results, metadata
        
        Returns:
            Manifest location and ID
        """
        operation_type = params.get("operation", "backfill")
        results = params.get("results", {})
        metadata = params.get("metadata", {})
        
        manifest_id = f"{operation_type}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        manifest = {
            "manifest_id": manifest_id,
            "operation": operation_type,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "metadata": metadata,
            "environment": {
                "project_id": self.settings.project_id,
                "workspace_id": self.settings.workspace_id,
                "agent_version": "1.0.0",
            },
        }
        
        # Store manifest (in production, this would write to S3/storage)
        manifest_path = f"artifacts/manifests/{manifest_id}.json"
        
        # Log manifest creation
        logger.info(f"Created manifest: {manifest_id}")
        
        return {
            "manifest_id": manifest_id,
            "location": manifest_path,
            "timestamp": manifest["timestamp"],
            "operation": operation_type,
        }
    
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
    
    # Phase 3: Data Operations Helper Methods
    
    def _simulate_table_analysis(self, table_name: str) -> Dict[str, Any]:
        """Simulate database table analysis."""
        # Common table patterns for simulation
        table_schemas = {
            "positions": {
                "columns": [
                    {"name": "id", "type": "INTEGER", "nullable": False},
                    {"name": "ticker", "type": "VARCHAR(10)", "nullable": False},
                    {"name": "quantity", "type": "DECIMAL(15,2)", "nullable": False},
                    {"name": "avg_price", "type": "DECIMAL(15,4)", "nullable": True},
                    {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                ],
                "primary_key": "id",
                "row_count": 1000,
                "indexes": ["ticker", "created_at"],
            },
            "trades": {
                "columns": [
                    {"name": "trade_id", "type": "VARCHAR(36)", "nullable": False},
                    {"name": "symbol", "type": "VARCHAR(10)", "nullable": False},
                    {"name": "quantity", "type": "INTEGER", "nullable": False},
                    {"name": "price", "type": "DECIMAL(15,4)", "nullable": False},
                    {"name": "trade_date", "type": "DATE", "nullable": False},
                ],
                "primary_key": "trade_id",
                "row_count": 50000,
                "indexes": ["symbol", "trade_date"],
            },
        }
        
        # Default schema if table not in predefined list
        default_schema = {
            "columns": [
                {"name": "id", "type": "INTEGER", "nullable": False},
                {"name": "name", "type": "VARCHAR(255)", "nullable": True},
                {"name": "value", "type": "DECIMAL(15,2)", "nullable": True},
                {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
            ],
            "primary_key": "id",
            "row_count": 100,
            "indexes": ["created_at"],
        }
        
        return table_schemas.get(table_name.lower(), default_schema)
    
    def _generate_pure_from_schema(
        self,
        model_name: str,
        columns: List[Dict[str, Any]],
        constraints: List[str] = None,
    ) -> str:
        """Generate PURE code from database schema."""
        properties = []
        
        for column in columns:
            col_name = column.get("name", "")
            col_type = column.get("type", "VARCHAR")
            nullable = column.get("nullable", True)
            
            # Map SQL types to PURE types
            pure_type = self._sql_to_pure_type(col_type)
            multiplicity = "[0..1]" if nullable else "[1]"
            
            properties.append(f"  {col_name}: {pure_type}{multiplicity};")
        
        # Add constraints if provided
        constraint_lines = []
        if constraints:
            for constraint in constraints:
                if constraint == "qtyPositive":
                    constraint_lines.append("  constraint qtyPositive: $this.quantity > 0;")
                elif constraint == "validTicker":
                    constraint_lines.append("  constraint validTicker: $this.ticker->isNotEmpty();")
                # Add more constraint patterns as needed
        
        pure = f"""Class model::{model_name}
{{
{chr(10).join(properties)}
{chr(10).join(constraint_lines) if constraint_lines else ''}
}}"""
        
        return pure
    
    def _sql_to_pure_type(self, sql_type: str) -> str:
        """Map SQL types to PURE types."""
        sql_type_upper = sql_type.upper()
        
        if "INT" in sql_type_upper:
            return "Integer"
        elif "DECIMAL" in sql_type_upper or "NUMERIC" in sql_type_upper:
            return "Float"
        elif "VARCHAR" in sql_type_upper or "TEXT" in sql_type_upper:
            return "String"
        elif "DATE" in sql_type_upper and "TIME" not in sql_type_upper:
            return "StrictDate"
        elif "TIMESTAMP" in sql_type_upper or "DATETIME" in sql_type_upper:
            return "DateTime"
        elif "BOOL" in sql_type_upper:
            return "Boolean"
        else:
            return "String"  # Default fallback
    
    def _columns_to_properties(self, columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert database columns to PURE properties."""
        properties = []
        
        for column in columns:
            col_name = column.get("name", "")
            col_type = column.get("type", "VARCHAR")
            nullable = column.get("nullable", True)
            
            pure_type = self._sql_to_pure_type(col_type)
            
            properties.append({
                "name": col_name,
                "type": pure_type,
                "multiplicity": {
                    "lowerBound": 0 if nullable else 1,
                    "upperBound": 1,
                },
            })
        
        return properties
    
    async def _analyze_data_source(self, data_source: str) -> Dict[str, Any]:
        """Analyze data source to determine size and structure."""
        # Parse data source (S3, file path, database, etc.)
        if data_source.startswith("s3://"):
            # Simulate S3 analysis
            return {
                "type": "s3",
                "total_records": 1000000,
                "total_size_mb": 500,
                "file_count": 100,
                "format": "csv",
            }
        elif data_source.startswith("file://") or "/" in data_source:
            # Simulate file analysis
            return {
                "type": "file",
                "total_records": 10000,
                "total_size_mb": 5,
                "file_count": 1,
                "format": "csv",
            }
        else:
            # Default for unknown sources
            return {
                "type": "unknown",
                "total_records": 1000,
                "total_size_mb": 1,
                "file_count": 1,
                "format": "json",
            }
    
    async def _process_window(
        self,
        window: Dict[str, Any],
        target_model: str,
        validate: bool = True,
    ) -> Dict[str, Any]:
        """Process a single data window."""
        window_id = window.get("window_id", 0)
        record_count = window.get("record_count", 0)
        
        # Simulate processing with some random failures
        import random
        
        failed_count = random.randint(0, max(1, record_count // 100))  # 0-1% failure rate
        processed_count = record_count - failed_count
        
        errors = []
        if failed_count > 0:
            errors.append(f"Window {window_id}: {failed_count} records failed validation")
        
        return {
            "window_id": window_id,
            "processed": processed_count,
            "failed": failed_count,
            "errors": errors,
            "status": "completed" if failed_count == 0 else "completed_with_errors",
        }
    
    def _apply_validation_rule(self, rule: str, sample_size: int) -> Dict[str, Any]:
        """Apply a validation rule to sample data."""
        # Simulate validation rules
        validation_rules = {
            "not_null": {"passed": True, "message": "All required fields present"},
            "valid_range": {"passed": True, "message": "Values within expected range"},
            "format_check": {"passed": True, "message": "Data formats valid"},
            "referential_integrity": {"passed": False, "message": "5 records have invalid references"},
        }
        
        return validation_rules.get(
            rule,
            {"passed": True, "message": f"Rule {rule} passed", "rule": rule}
        )