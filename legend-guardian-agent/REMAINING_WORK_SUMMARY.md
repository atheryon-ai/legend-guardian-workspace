# Legend Guardian Agent - Remaining Work Summary

**Last Updated**: After API Research (see LEGEND_API_RESEARCH.md)

## Critical Assessment: What's Still Missing

### 🔴 CRITICAL BLOCKERS (Phase 1) - These break multiple use cases
These handlers are referenced in the flows.py router but DO NOT EXIST in orchestrator.py:

1. **`_compile`** - MISSING (BUT CLIENT METHOD EXISTS)
   - Used by: UC1, UC2, UC4, UC5, UC6, UC8
   - Impact: Nothing can be validated without compilation
   - Priority: HIGHEST
   - **UPDATE**: Engine client has `compile()` method, needs workspace→PURE conversion

2. **`_generate_service`** - MISSING (REQUIRES REDESIGN)
   - Used by: UC1
   - Impact: Cannot create REST endpoints
   - Priority: HIGHEST
   - **UPDATE**: Services are NOT generated via API - must create service definitions in model

3. **`_open_review`** - MISSING (NEEDS GITLAB INTEGRATION)
   - Used by: UC1, UC2
   - Impact: Cannot create PRs/merge requests
   - Priority: HIGHEST
   - **UPDATE**: Requires GitLab API integration in SDLCClient

### 🟡 IMPORTANT GAPS (Phase 2) - Model Management
These are needed for specific use cases:

4. **`_create_mapping`** - MISSING
   - Used by: UC1
   - Impact: Cannot map CSV data to models

5. **`_apply_changes`** - MISSING
   - Used by: UC2
   - Impact: Cannot evolve models safely

6. **`_create_service`** - MISSING
   - Used by: UC3
   - Impact: Cannot create services from imported models

7. **`_create_v2_service`** - MISSING
   - Used by: UC2
   - Impact: Cannot version services

8. **`_schema_to_model`** - MISSING
   - Used by: UC6
   - Impact: Cannot generate from JSON Schema

### ✅ COMPLETED (Phase 3) - Data Operations
All handlers for UC4 and UC7 are complete:
- `_analyze_table` ✅
- `_generate_model` ✅
- `_add_constraints` ✅
- `_plan_ingestion` ✅
- `_execute_backfill` ✅
- `_validate_sample` ✅
- `_record_manifest` ✅

### 🟠 REMAINING PHASES

#### Phase 4: Governance & Testing (UC5, UC6)
- `_enumerate_entities` - List all models/services
- `_compile_all` - Bulk compilation
- `_run_constraint_tests` - Constraint validation
- `_generate_evidence_bundle` - Audit evidence
- `_generate_positive_tests` - Happy path tests
- `_generate_negative_tests` - Error case tests
- `_attach_schema_bundle` - Schema documentation

#### Phase 5: Advanced Operations (UC8)
- `_list_versions` - Version history
- `_find_last_good_version` - Auto-detect stable version
- `_create_hotfix_workspace` - Emergency workspace
- `_revert_to_version` - Rollback mechanism
- `_flip_traffic` - Blue-green deployment

#### Phase 6: Production Features (UC4 remainder)
- `_create_data_product` - Data product publishing
- `_export_schema` - Schema export (JSON/Avro)

## Use Case Readiness Assessment

| Use Case | Status | Missing Handlers | Can Run? |
|----------|--------|-----------------|----------|
| UC1: Ingest→Publish | 🔴 BLOCKED | _compile, _generate_service, _open_review, _create_mapping | NO |
| UC2: Safe Rollout | 🔴 BLOCKED | _compile, _open_review, _apply_changes, _create_v2_service | NO |
| UC3: Model Reuse | 🟡 PARTIAL | _create_service | PARTIAL |
| UC4: Reverse ETL | 🟡 PARTIAL | _compile, _create_data_product, _export_schema | PARTIAL |
| UC5: Governance | 🔴 BLOCKED | ALL handlers missing | NO |
| UC6: Contract-first | 🔴 BLOCKED | ALL handlers missing | NO |
| UC7: Bulk Backfill | ✅ COMPLETE | None | YES* |
| UC8: Incident Response | 🔴 BLOCKED | ALL handlers missing | NO |

*UC7 can run but won't compile results without _compile handler

## Test Script Status

| Script | Status | Runnable? |
|--------|--------|-----------|
| usecase1_ingest_publish.sh | ✅ Exists | 🔴 Will fail (missing handlers) |
| usecase2_safe_rollout.sh | ✅ Exists | 🔴 Will fail (missing handlers) |
| usecase3_model_reuse.sh | ✅ Exists | 🟡 Partial (will fail at service creation) |
| usecase4_reverse_etl.sh | ✅ Exists | 🟡 Partial (will fail at compile) |
| usecase5_governance_audit.sh | ❌ Missing | N/A |
| usecase6_contract_first.sh | ❌ Missing | N/A |
| usecase7_bulk_backfill.sh | ✅ Exists | ✅ Should work |
| usecase8_incident_rollback.sh | ❌ Missing | N/A |

## Prioritized Completion Roadmap

### 🚨 IMMEDIATE (Block everything)
**Goal**: Unblock UC1, UC2, UC4
```python
1. Implement _compile()
2. Implement _generate_service()  
3. Implement _open_review()
```

### HIGH PRIORITY (Complete UC1)
**Goal**: Make UC1 fully functional
```python
4. Implement _create_mapping()
```

### MEDIUM PRIORITY (Complete UC2, UC3)
**Goal**: Enable model evolution and reuse
```python
5. Implement _apply_changes()
6. Implement _create_v2_service()
7. Implement _create_service()
```

### LOWER PRIORITY (New use cases)
**Goal**: Enable UC5, UC6, UC8
```python
8-20. Implement remaining handlers per phase plan
```

## Recommended Next Action (REVISED)

### Based on API Research:

**1. IMPLEMENT `_compile` NOW** ✅ Can be done immediately
```python
# Use existing engine_client.compile() with workspace entity conversion
```

**2. REDESIGN `_generate_service`** 🟡 Requires different approach
```python
# Create service definition entities in workspace
# Services are built/deployed via SDLC pipeline, not API
```

**3. ADD GITLAB INTEGRATION for `_open_review`** 🟡 Requires new client methods
```python
# Add GitLab MR API wrapper to SDLCClient
# Use OAuth with configured GitLab application
```

### Implementation Feasibility:
- ✅ **Can implement now**: `_compile` (with entity conversion)
- 🟡 **Needs redesign**: `_generate_service` (create definitions, not generate)
- 🟡 **Needs client extension**: `_open_review` (add GitLab API methods)

Without these, the agent is essentially non-functional for its primary purpose of orchestrating Legend operations.

## Success Metrics

Current Implementation: **~35% Complete**
- ✅ Phase 3 (Data Operations): 100%
- 🟡 Phase 1 (Core): 0% (but path forward identified)
- 🔴 Phase 2 (Model Management): 14% (1/7 done - _add_constraints)
- 🔴 Phase 4 (Governance): 0%
- 🔴 Phase 5 (Advanced): 0%
- 🔴 Phase 6 (Production): 0%

**To reach MVP (60%)**: Implement Phase 1 + Phase 2
**To reach Production (100%)**: Complete all 6 phases

## Key Learnings from API Research

1. **Service Generation**: Not an API operation - services defined in models, built via SDLC
2. **Compilation**: Endpoint exists, needs entity-to-PURE conversion
3. **Reviews**: Standard GitLab MR API, needs OAuth setup
4. **Architecture**: Legend uses declarative service definitions, not imperative generation

See `LEGEND_API_RESEARCH.md` for detailed findings.