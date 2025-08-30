# Phase 1: Core Compilation & Service Generation - Review

## Overview
Phase 1 contains the three most critical handlers that block 6 out of 8 use cases. These handlers are fundamental to the Legend Guardian Agent's ability to orchestrate Legend platform operations.

## Handler Analysis

### 1. ✅ `_compile` Handler
**Status**: READY TO IMPLEMENT
**Client Method**: `engine_client.compile()` EXISTS at `src/clients/engine.py:86-130`

**Current Implementation in EngineClient:**
```python
async def compile(
    self,
    pure: str,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]
```

**Problem**: The orchestrator expects to compile code already in a workspace, but the engine client expects raw PURE code as input.

**Solution Needed**:
1. First fetch entities from workspace using SDLC client
2. Convert entities to PURE code
3. Pass PURE to engine compile method

### 2. ❌ `_generate_service` Handler  
**Status**: MISSING CLIENT METHOD
**Client Method**: NO `generate_service()` method in EngineClient

**Available Alternative**: `run_service()` at line 242 - but this RUNS existing services, doesn't generate them.

**Solution Needed**:
1. Add `generate_service()` method to EngineClient
2. Research correct Legend Engine API endpoint for service generation
3. May need to create service definition in SDLC first, then deploy via Engine

### 3. ❌ `_open_review` Handler
**Status**: MISSING CLIENT METHOD
**Client Method**: NO review/PR methods in SDLCClient

**Solution Needed**:
1. Add `create_review()` method to SDLCClient
2. Implement GitLab/GitHub integration for PR creation
3. Handle workspace-to-master merge request flow

## Implementation Status

| Handler | Client Method | Status | Blocker |
|---------|--------------|--------|---------|
| `_compile` | `engine_client.compile()` | ✅ Exists | Need workspace→PURE conversion |
| `_generate_service` | Missing | ❌ | No client method |
| `_open_review` | Missing | ❌ | No client method |

## Missing Client Methods Discovery

### EngineClient Missing:
- `generate_service()` - Service generation from model/mapping
- `deploy_service()` - Service deployment 
- `create_service_definition()` - Service specification

### SDLCClient Missing:
- `create_review()` - Create merge request/PR
- `get_reviews()` - List reviews
- `merge_review()` - Merge approved review
- `get_workspace_diff()` - Get changes for review

## Detailed Implementation Requirements

### 1. _compile Handler Implementation

```python
async def _compile(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Compile PURE code in workspace."""
    project_id = params.get("project_id", self.settings.project_id)
    workspace_id = params.get("workspace_id", self.settings.workspace_id)
    
    # Step 1: Get entities from workspace
    entities = await self.sdlc_client.get_entities(
        project_id=project_id,
        workspace_id=workspace_id
    )
    
    # Step 2: Convert entities to PURE
    pure_code = self._entities_to_pure(entities)
    
    # Step 3: Compile PURE
    result = await self.engine_client.compile(
        pure=pure_code,
        project_id=project_id,
        workspace_id=workspace_id
    )
    
    return {
        "status": "success" if result.get("status") == "success" else "failed",
        "result": result,
        "errors": result.get("errors", [])
    }
```

### 2. _generate_service Handler Implementation

**BLOCKED**: Need to add method to EngineClient first

Research needed:
- Legend Engine API endpoint for service generation
- Required parameters (model, mapping, runtime, query)
- Service deployment process

Potential endpoints to investigate:
- `/api/pure/v1/service/generate`
- `/api/pure/v1/execution/service`
- `/api/legend/service/v1/generate`

### 3. _open_review Handler Implementation

**BLOCKED**: Need to add method to SDLCClient first

Research needed:
- GitLab API integration for MR creation
- Required OAuth scopes
- Workspace diff generation
- Review metadata requirements

Potential implementation:
```python
async def create_review(
    self,
    project_id: str,
    workspace_id: str,
    title: str,
    description: str = "",
) -> Dict[str, Any]:
    """Create merge request from workspace to master."""
    # Need GitLab/GitHub API integration
    pass
```

## Next Steps

### Immediate Actions:
1. ✅ Implement `_compile` handler using existing engine client method
2. ❌ Research Legend Engine API for service generation endpoints
3. ❌ Research Legend SDLC API for review/MR endpoints

### Required Research:
1. **Service Generation**: 
   - Check Legend Engine documentation for service generation API
   - Review Legend Studio source code for service creation flow
   - Test endpoints manually with curl/httpie

2. **Review Creation**:
   - Check Legend SDLC documentation for GitLab integration
   - Review Legend SDLC source for review workflow
   - Understand workspace→master merge process

### Implementation Order:
1. **First**: Implement `_compile` (can be done now)
2. **Second**: Add missing client methods based on research
3. **Third**: Implement `_generate_service` and `_open_review`

## Risk Assessment

### High Risk:
- **Service Generation**: May require complex multi-step process
- **Review Creation**: Requires external Git provider integration

### Medium Risk:
- **Compilation**: Entity to PURE conversion may have edge cases

### Mitigation:
1. Start with `_compile` implementation (lowest risk)
2. Create mock implementations for missing methods
3. Document API research findings
4. Consider fallback strategies (manual service creation, CLI-based PR)

## Conclusion

Phase 1 is partially blocked:
- ✅ `_compile` can be implemented immediately
- ❌ `_generate_service` needs client method research/addition
- ❌ `_open_review` needs client method research/addition

The compilation handler can unblock some testing, but full Phase 1 completion requires adding missing client methods based on Legend API research.