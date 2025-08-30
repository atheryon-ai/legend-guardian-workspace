# Legend Guardian Agent - Placeholder Completion Plan

## Executive Summary
After reviewing all 8 use cases, I've identified that while API endpoints exist for all use cases, many critical handler methods in the orchestrator are missing. The flows.py router calls `orchestrator.execute_step()` but many of the required step handlers are placeholders or missing entirely.

## Missing Handler Methods in Orchestrator

### Use Case 1: Ingest → Publish ✅ 
**Status**: MOSTLY COMPLETE
- ✅ `_create_workspace` - Implemented at line 199
- ✅ `_create_model` - Implemented at line 206
- ❌ `_create_mapping` - MISSING
- ❌ `_compile` - MISSING (critical)
- ❌ `_generate_service` - MISSING
- ❌ `_open_review` - MISSING

### Use Case 2: Safe Rollout
**Status**: MOSTLY MISSING
- ✅ `_create_workspace` - Reused from UC1
- ❌ `_apply_changes` - MISSING (critical for model evolution)
- ❌ `_compile` - MISSING
- ✅ `_run_tests` - Implemented at line 393
- ❌ `_create_v2_service` - MISSING
- ❌ `_open_review` - MISSING

### Use Case 3: Model Reuse
**Status**: PARTIALLY COMPLETE
- ✅ `_search_depot` - Implemented at line 310
- ✅ `_import_model` - Implemented at line 315
- ✅ `_transform_schema` - Implemented at line 381
- ❌ `_create_service` - MISSING

### Use Case 4: Reverse ETL
**Status**: ALL MISSING
- ❌ `_analyze_table` - MISSING (DB introspection)
- ❌ `_generate_model` - MISSING (differs from create_model)
- ❌ `_add_constraints` - MISSING
- ❌ `_compile` - MISSING
- ❌ `_create_data_product` - MISSING
- ❌ `_export_schema` - MISSING

### Use Case 5: Governance Audit
**Status**: ALL MISSING
- ❌ `_enumerate_entities` - MISSING
- ❌ `_compile_all` - MISSING
- ❌ `_run_constraint_tests` - MISSING
- ❌ `_generate_evidence_bundle` - MISSING

### Use Case 6: Contract-first API
**Status**: ALL MISSING
- ❌ `_schema_to_model` - MISSING (JSON Schema → PURE)
- ❌ `_compile` - MISSING
- ❌ `_generate_positive_tests` - MISSING
- ❌ `_generate_negative_tests` - MISSING
- ❌ `_publish_service` - MISSING
- ❌ `_attach_schema_bundle` - MISSING

### Use Case 7: Bulk Backfill
**Status**: ALL MISSING
- ❌ `_plan_ingestion` - MISSING
- ❌ `_validate_sample` - MISSING
- ❌ `_execute_backfill` - MISSING
- ❌ `_record_manifest` - MISSING

### Use Case 8: Incident Rollback
**Status**: ALL MISSING
- ❌ `_list_versions` - MISSING
- ❌ `_find_last_good_version` - MISSING
- ❌ `_create_hotfix_workspace` - MISSING
- ❌ `_revert_to_version` - MISSING
- ❌ `_compile` - MISSING
- ❌ `_flip_traffic` - MISSING

## Implementation Priority Plan

### Phase 1: Core Compilation & Service Generation (Critical Path)
**Timeline**: Immediate
**Why**: These are used across multiple use cases

1. **`_compile`** - Required by UC 1, 2, 4, 5, 6, 8
   ```python
   async def _compile(self, params: Dict[str, Any]) -> Dict[str, Any]:
       """Compile PURE code in workspace."""
       result = await self.engine_client.compile(
           project_id=params.get("project_id", self.settings.project_id),
           workspace_id=params.get("workspace_id", self.settings.workspace_id)
       )
       return {"status": "success" if result else "failed", "result": result}
   ```

2. **`_generate_service`** - Required by UC 1
   ```python
   async def _generate_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
       """Generate REST service endpoint."""
       service_path = params.get("path", "generated/service")
       result = await self.engine_client.generate_service(
           project_id=self.settings.project_id,
           workspace_id=self.settings.workspace_id,
           service_path=service_path,
           query=params.get("query")
       )
       return {"service_path": service_path, "url": f"{self.settings.engine_url}/api/service/{service_path}"}
   ```

3. **`_open_review`** - Required by UC 1, 2
   ```python
   async def _open_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
       """Open merge request/PR."""
       title = params.get("title", "Agent-generated changes")
       result = await self.sdlc_client.create_review(
           project_id=self.settings.project_id,
           workspace_id=self.settings.workspace_id,
           title=title,
           description=params.get("description", "")
       )
       return {"review_id": result.get("id"), "url": result.get("web_url")}
   ```

### Phase 2: Model Management
**Timeline**: Day 2

4. **`_create_mapping`** - UC 1
5. **`_apply_changes`** - UC 2 (model evolution)
6. **`_add_constraints`** - UC 4
7. **`_schema_to_model`** - UC 6

### Phase 3: Data Operations ✅ COMPLETED
**Timeline**: Day 3

8. **`_analyze_table`** - UC 4 (database introspection) ✅
9. **`_generate_model`** - UC 4 (from DB schema) ✅
10. **`_add_constraints`** - UC 4 ✅
11. **`_plan_ingestion`** - UC 7 ✅
12. **`_execute_backfill`** - UC 7 ✅
13. **`_validate_sample`** - UC 7 ✅
14. **`_record_manifest`** - UC 7 ✅

### Phase 4: Governance & Testing
**Timeline**: Day 4

12. **`_enumerate_entities`** - UC 5
13. **`_compile_all`** - UC 5
14. **`_run_constraint_tests`** - UC 5
15. **`_generate_positive_tests`** - UC 6
16. **`_generate_negative_tests`** - UC 6

### Phase 5: Advanced Operations
**Timeline**: Day 5

17. **`_list_versions`** - UC 8
18. **`_find_last_good_version`** - UC 8
19. **`_revert_to_version`** - UC 8
20. **`_flip_traffic`** - UC 8 (blue-green deployment)

### Phase 6: Production Features
**Timeline**: Day 6

21. **`_create_data_product`** - UC 4
22. **`_export_schema`** - UC 4
23. **`_generate_evidence_bundle`** - UC 5
24. **`_attach_schema_bundle`** - UC 6
25. **`_record_manifest`** - UC 7

## Test Harness Completion

### Test Scripts Status:
1. `usecase1_ingest_publish.sh` - ✅ Complete
2. `usecase2_safe_rollout.sh` - ✅ Complete
3. `usecase3_model_reuse.sh` - ✅ Complete
4. `usecase4_reverse_etl.sh` - ✅ Complete (Phase 3)
5. `usecase5_governance_audit.sh` - ❌ Missing
6. `usecase6_contract_first.sh` - ❌ Missing
7. `usecase7_bulk_backfill.sh` - ✅ Complete (Phase 3)
8. `usecase8_incident_rollback.sh` - ❌ Missing

## Success Criteria

Each use case should:
1. ✅ Create workspace successfully
2. ✅ Perform all transformations
3. ✅ Compile without errors
4. ✅ Return expected JSON structure
5. ✅ Handle errors gracefully
6. ✅ Generate correlation IDs
7. ✅ Support both JWT and API key auth

## Risk Mitigation

1. **Compilation Failures**: Implement retry logic with error details
2. **Service Generation**: Validate PURE before generation
3. **Version Management**: Implement proper Git tagging
4. **Rollback Safety**: Test in isolated workspaces first
5. **Data Validation**: Sample validation before bulk operations

## Next Steps

1. **Immediate**: Implement Phase 1 handlers (_compile, _generate_service, _open_review)
2. **Day 2-3**: Complete model and data operation handlers
3. **Day 4-5**: Add governance and advanced features
4. **Day 6**: Production hardening and test scripts
5. **Final**: End-to-end testing of all 8 use cases

## Validation Command

After implementation, validate with:
```bash
# Test all use cases
for i in {1..8}; do
  echo "Testing Use Case $i"
  ./artifacts/harness/usecase${i}_*.sh
done
```