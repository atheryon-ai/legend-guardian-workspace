
from typing import Dict, Any, List

from typing import Dict, Any, List
import json
from src.clients.engine import engine_client
from src.clients.sdlc import sdlc_client
from src.clients.depot import depot_client
from src.agent.memory import memory

from src.agent.policies import policy

from src.agent.llm_client import llm_client

class Orchestrator:
    def _generate_dummy_entities(self, source: str, target: str) -> List[Dict]:
        """Generates dummy PURE entities for a given source and target."""
        return [
            {
                "path": f"data::{source}_Store",
                "classifierPath": "meta::pure::store::flatData::FlatData",
                "content": {
                    "name": f"{source}_Store",
                    "package": "data",
                    "url": f"data/{source}.csv"
                }
            },
            {
                "path": f"domain::{target}",
                "classifierPath": "meta::pure::metamodel::type::Class",
                "content": {
                    "name": target,
                    "package": "domain",
                    "properties": [
                        {"name": "id", "type": "String"},
                        {"name": "notional", "type": "Float"}
                    ]
                }
            }
        ]

    async def _create_mapping(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Creates a mapping between a source and target class."""
        source_class = params.get("source_class")
        target_class = params.get("target_class")

        property_mappings = []
        for prop in source_class.get("properties", []):
            prop_name = prop.get("name")
            if any(p.get("name") == prop_name for p in target_class.get("properties", [])):
                property_mappings.append(f"{prop_name}: {prop_name}")

        mapping_entity = {
            "path": f"mappings::{source_class.get('name')}To{target_class.get('name')}Mapping",
            "classifierPath": "meta::pure::mapping::Mapping",
            "content": {
                "name": f"{source_class.get('name')}To{target_class.get('name')}Mapping",
                "package": "mappings",
                "classMappings": [
                    {
                        "class": f"domain::{target_class.get('name')}",
                        "root": True,
                        "propertyMappings": property_mappings
                    }
                ]
            }
        }
        
        await sdlc_client.upsert_entities(project_id, workspace_id, [mapping_entity])
        return {"status": "success", "entity": mapping_entity}

    async def _apply_changes(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Applies changes to a model in a workspace."""
        # Placeholder implementation
        print(f"Applying changes: {params.get('changes')}")
        return {"status": "success"}

    async def _add_constraints(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Adds constraints to a model."""
        # Placeholder implementation
        print(f"Adding constraints: {params.get('constraints')}")
        return {"status": "success"}

    async def _schema_to_model(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generates a PURE model from a schema."""
        # Placeholder implementation
        print(f"Generating model from schema: {params.get('schema')}")
        return {"status": "success"}

    async def _analyze_table(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Analyzes a database table and returns its schema."""
        table_name = params.get("table_name")
        # Placeholder for database connection and introspection
        dummy_schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "varchar"},
                {"name": "amount", "type": "decimal"}
            ]
        }
        return {"status": "success", "schema": dummy_schema}

    async def _generate_model(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generates a PURE model from a database schema."""
        schema = params.get("schema")
        # Placeholder implementation
        dummy_model = {
            "path": "domain::MyNewModel",
            "classifierPath": "meta::pure::metamodel::type::Class",
            "content": {
                "name": "MyNewModel",
                "package": "domain",
                "properties": schema.get("columns", [])
            }
        }
        return {"status": "success", "model": dummy_model}

    async def _plan_ingestion(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Plans a bulk ingestion process."""
        # Placeholder implementation
        dummy_plan = {
            "steps": [
                {"action": "ingest_chunk_1"},
                {"action": "ingest_chunk_2"},
                {"action": "ingest_chunk_3"}
            ]
        }
        return {"status": "success", "plan": dummy_plan}

    async def _execute_backfill(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Executes a backfill process based on an ingestion plan."""
        # Placeholder implementation
        ingestion_plan = params.get("plan")
        print(f"Executing backfill with plan: {ingestion_plan}")
        return {"status": "success"}

    async def _enumerate_entities(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Enumerates all entities in a workspace."""
        entities = await sdlc_client.get_entities(project_id, workspace_id)
        return {"status": "success", "entities": entities}

    async def _compile_all(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Compiles all entities in a workspace."""
        entities_response = await self._enumerate_entities(params, project_id, workspace_id)
        entities = entities_response.get("entities", [])
        pure_code = json.dumps(entities)
        result = await engine_client.compile(
            project_id=project_id,
            workspace_id=workspace_id,
            pure_code=pure_code
        )
        return {"status": "success" if result.get("status") != "error" else "failed", "result": result}

    async def _run_constraint_tests(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Runs constraint tests on a model."""
        # Placeholder implementation
        print(f"Running constraint tests: {params.get('tests')}")
        return {"status": "success"}

    async def _generate_positive_tests(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generates positive test data for a service."""
        # Placeholder implementation
        print(f"Generating positive tests for service: {params.get('service')}")
        return {"status": "success", "tests": []}

    async def _generate_negative_tests(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generates negative test data for a service."""
        # Placeholder implementation
        print(f"Generating negative tests for service: {params.get('service')}")
        return {"status": "success", "tests": []}

    async def _list_versions(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Lists all versions of a project."""
        versions = await depot_client.list_versions(project_id)
        return {"status": "success", "versions": versions}

    async def _find_last_good_version(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Finds the last good version of a project."""
        # Placeholder implementation
        return {"status": "success", "version": "1.0.0"}

    async def _revert_to_version(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Reverts a project to a specific version."""
        # Placeholder implementation
        print(f"Reverting to version: {params.get('version')}")
        return {"status": "success"}

    async def _flip_traffic(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Flips traffic to a different version of a service."""
        # Placeholder implementation
        print(f"Flipping traffic to version: {params.get('version')}")
        return {"status": "success"}

    async def _create_data_product(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Creates a new data product."""
        # Placeholder implementation
        print(f"Creating data product: {params.get('name')}")
        return {"status": "success"}

    async def _export_schema(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Exports the schema of a data product."""
        # Placeholder implementation
        return {"status": "success", "schema": {}}

    async def _generate_evidence_bundle(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generates an evidence bundle for a governance audit."""
        # Placeholder implementation
        return {"status": "success", "bundle": {}}

    async def _attach_schema_bundle(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Attaches a schema bundle to a service."""
        # Placeholder implementation
        return {"status": "success"}

    async def _record_manifest(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Records a manifest of a backfill operation."""
        # Placeholder implementation
        return {"status": "success"}

    async def _compile(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Compile PURE code in workspace."""
        result = await engine_client.compile(
            project_id=project_id,
            workspace_id=workspace_id,
            pure_code=params.get("pure_code", "")
        )
        return {"status": "success" if result.get("status") != "error" else "failed", "result": result}

    async def _generate_service(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Generate REST service endpoint."""
        service_path = params.get("path", "generated/service")
        result = await engine_client.generate_service(
            project_id=project_id,
            workspace_id=workspace_id,
            service_path=service_path,
            query=params.get("query", "")
        )
        return {"service_path": service_path, "url": f"/api/service/{service_path}"}

    async def _open_review(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Open merge request/PR."""
        title = params.get("title", "Agent-generated changes")
        result = await sdlc_client.open_review(
            project_id=project_id,
            workspace_id=workspace_id,
            title=title,
            description=params.get("description", "")
        )
        return {"review_id": result.get("id"), "url": result.get("webUrl")}

    async def _upsert_entities(self, params: Dict[str, Any], project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Upsert entities in a workspace."""
        entities = self._generate_dummy_entities(params["source"], params["target"])
        result = await sdlc_client.upsert_entities(
            project_id=project_id,
            workspace_id=workspace_id,
            entities=entities
        )
        return {"status": "success", "result": result, "entities": entities}

    async def create_plan(self, prompt: str, project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Creates a plan from a user prompt using the LLM client."""
        pii_warnings = policy.check_pii(prompt)
        if pii_warnings:
            # Handle PII, for now just log a warning
            print(f"PII Warning: {pii_warnings}")

        return await llm_client.parse_intent(prompt)

    async def execute_plan(self, plan: Dict[str, Any], prompt: str, project_id: str, workspace_id: str) -> Dict[str, Any]:
        """Executes a plan and saves the episode."""
        logs = []
        artifacts = []
        entities = []
        
        handler_map = {
            "engine.compile": self._compile,
            "engine.compile_all": self._compile_all,
            "engine.run_constraint_tests": self._run_constraint_tests,
            "engine.generate_positive_tests": self._generate_positive_tests,
            "engine.generate_negative_tests": self._generate_negative_tests,
            "engine.generate_service": self._generate_service,
            "sdlc.open_review": self._open_review,
            "sdlc.upsert_entities": self._upsert_entities,
            "sdlc.create_mapping": self._create_mapping,
            "sdlc.apply_changes": self._apply_changes,
            "sdlc.add_constraints": self._add_constraints,
            "sdlc.schema_to_model": self._schema_to_model,
            "sdlc.enumerate_entities": self._enumerate_entities,
            "sdlc.list_versions": self._list_versions,
            "sdlc.find_last_good_version": self._find_last_good_version,
            "sdlc.revert_to_version": self._revert_to_version,
            "sdlc.flip_traffic": self._flip_traffic,
            "sdlc.create_data_product": self._create_data_product,
            "sdlc.export_schema": self._export_schema,
            "sdlc.generate_evidence_bundle": self._generate_evidence_bundle,
            "sdlc.attach_schema_bundle": self._attach_schema_bundle,
            "sdlc.record_manifest": self._record_manifest,
            "db.analyze_table": self._analyze_table,
            "db.generate_model": self._generate_model,
            "ingestion.plan": self._plan_ingestion,
            "ingestion.execute_backfill": self._execute_backfill,
        }

        client_map = {
            "engine": engine_client,
            "sdlc": sdlc_client,
            "depot": depot_client
        }

        for step in plan.get("steps", []):
            action = step.get("action")
            params = step.get("params", {})
            
            if action == "engine.compile":
                params["pure_code"] = json.dumps(entities)

            handler = handler_map.get(action)
            if handler:
                try:
                    result = await handler(params, project_id, workspace_id)
                    if action == "sdlc.upsert_entities":
                        entities = result.get("entities", [])
                    logs.append(f"Successfully executed {action}")
                    artifacts.append({"action": action, "status": "success", "result": result})
                except Exception as e:
                    logs.append(f"Error executing {action}: {e}")
                    artifacts.append({"action": action, "status": "error", "message": str(e)})
            else:
                # Fallback to direct client call for now
                client_name, method_name = action.split(".")
                client = client_map.get(client_name)
                method = getattr(client, method_name, None)
                if client and method:
                    try:
                        if 'project_id' not in params:
                            params['project_id'] = project_id
                        if 'workspace_id' not in params:
                            params['workspace_id'] = workspace_id

                        result = await method(**params)
                        logs.append(f"Successfully executed {action}")
                        artifacts.append({"action": action, "status": "success", "result": result})
                    except Exception as e:
                        logs.append(f"Error executing {action}: {e}")
                        artifacts.append({"action": action, "status": "error", "message": str(e)})
                else:
                    logs.append(f"Action {action} not found")
                    artifacts.append({"action": action, "status": "error", "message": "Action not found"})
        
        results = {"logs": logs, "artifacts": artifacts}
        await memory.save_episode(prompt, plan, results)
        return results

# Export a module-level orchestrator instance expected by API routers
orchestrator = Orchestrator()
