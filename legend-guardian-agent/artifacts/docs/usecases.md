# Legend Guardian Agent - Use Cases Documentation

## Overview

This document describes the 8 primary use cases supported by the Legend Guardian Agent, including example requests and expected responses.

## Use Case 1: Ingest → Model → Map → Publish Service

**Description**: Complete end-to-end flow from CSV data ingestion to REST service publication.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase1/ingest-publish \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "csv_data": "id,ticker,quantity,price\n1,AAPL,100,150.50\n2,GOOGL,50,2800.00",
    "model_name": "Trade",
    "service_path": "trades/byNotional",
    "mapping_name": "TradeMapping"
  }'
```

### Response

```json
{
  "use_case": "ingest_publish",
  "status": "completed",
  "results": [
    {
      "action": "create_workspace",
      "result": {"workspace_id": "terry-dev", "created": true}
    },
    {
      "action": "create_model",
      "result": {"model": "Trade", "pure": "Class model::Trade {...}"}
    },
    {
      "action": "create_mapping",
      "result": {"mapping": "TradeMapping"}
    },
    {
      "action": "compile",
      "result": {"status": "success"}
    },
    {
      "action": "generate_service",
      "result": {"service_path": "trades/byNotional"}
    },
    {
      "action": "open_review",
      "result": {"review_id": "PR-123", "url": "http://..."}
    }
  ],
  "service_url": "http://localhost:6300/api/service/trades/byNotional",
  "correlation_id": "abc-123"
}
```

### Service Query

```bash
# Query the generated service
curl "http://localhost:6300/api/service/trades/byNotional?minNotional=10000"
```

## Use Case 2: Model Change with Safe Rollout

**Description**: Safely evolve models with backward compatibility and versioning.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase2/safe-rollout \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model_path": "model::Trade",
    "changes": {
      "rename": {"notional": "notionalAmount"},
      "add_field": {"name": "tradeDate", "type": "Date"}
    },
    "keep_v1": true
  }'
```

### Response

```json
{
  "use_case": "safe_rollout",
  "status": "completed",
  "results": [
    {
      "action": "create_workspace",
      "result": {"workspace_id": "terry-dev-v2"}
    },
    {
      "action": "apply_changes",
      "result": {"changes_applied": 2}
    },
    {
      "action": "compile",
      "result": {"status": "success"}
    },
    {
      "action": "run_tests",
      "result": {"passed": true, "tests": 15}
    },
    {
      "action": "create_v2_service",
      "result": {"v2_path": "trades/v2/byNotional"}
    },
    {
      "action": "open_review",
      "result": {"review_id": "PR-124"}
    }
  ],
  "v1_maintained": true,
  "correlation_id": "def-456"
}
```

## Use Case 3: Cross-bank Model Reuse via Depot

**Description**: Discover and reuse models from the depot with schema transformation.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase3/model-reuse \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "FXOption",
    "target_format": "avro",
    "service_name": "fx_options_service"
  }'
```

### Response

```json
{
  "use_case": "model_reuse",
  "status": "completed",
  "results": [
    {
      "action": "search_depot",
      "result": [
        {"project_id": "org.finos.fx", "path": "model::FXOption", "version": "1.0.0"}
      ]
    },
    {
      "action": "import_model",
      "result": {"imported": true}
    },
    {
      "action": "transform_schema",
      "result": {
        "schema": {
          "type": "record",
          "name": "FXOption",
          "fields": [...]
        }
      }
    },
    {
      "action": "create_service",
      "result": {"service": "fx_options_service"}
    }
  ],
  "schema_format": "avro",
  "correlation_id": "ghi-789"
}
```

## Use Case 4: Reverse ETL → Data Product

**Description**: Create data products from database tables with constraints.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase4/reverse-etl \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "source_table": "positions",
    "model_name": "Position",
    "constraints": ["qtyPositive", "validTicker"]
  }'
```

### Response

```json
{
  "use_case": "reverse_etl",
  "status": "completed",
  "results": [
    {
      "action": "analyze_table",
      "result": {
        "columns": ["id", "ticker", "quantity", "avg_price"],
        "row_count": 1000
      }
    },
    {
      "action": "generate_model",
      "result": {"model": "Position"}
    },
    {
      "action": "add_constraints",
      "result": {"constraints_added": 2}
    },
    {
      "action": "compile",
      "result": {"status": "success"}
    },
    {
      "action": "create_data_product",
      "result": {"product": "positions/latest"}
    },
    {
      "action": "export_schema",
      "result": {"schema": {...}}
    }
  ],
  "model_created": "Position",
  "correlation_id": "jkl-012"
}
```

## Use Case 5: Governance Audit & Lineage Proof

**Description**: Comprehensive audit with compliance evidence generation.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase5/governance-audit \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "all",
    "include_tests": true,
    "generate_evidence": true
  }'
```

### Response

```json
{
  "use_case": "governance_audit",
  "status": "completed",
  "results": [
    {
      "action": "enumerate_entities",
      "result": {
        "models": 25,
        "mappings": 15,
        "services": 10
      }
    },
    {
      "action": "compile_all",
      "result": {"compiled": 50, "failed": 0}
    },
    {
      "action": "run_constraint_tests",
      "result": {"passed": 48, "failed": 2}
    },
    {
      "action": "generate_evidence_bundle",
      "result": {
        "bundle_id": "audit-20240101-123456",
        "location": "artifacts/audit-bundle.zip"
      }
    }
  ],
  "audit_scope": "all",
  "evidence_generated": true,
  "correlation_id": "mno-345"
}
```

## Use Case 6: Contract-first API

**Description**: Generate API implementation from schema specification.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase6/contract-first \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "value": {"type": "number"}
      }
    },
    "service_path": "contracts/entity",
    "generate_tests": true
  }'
```

### Response

```json
{
  "use_case": "contract_first",
  "status": "completed",
  "results": [
    {
      "action": "schema_to_model",
      "result": {"model": "ContractEntity"}
    },
    {
      "action": "compile",
      "result": {"status": "success"}
    },
    {
      "action": "generate_positive_tests",
      "result": {"tests": 5}
    },
    {
      "action": "generate_negative_tests",
      "result": {"tests": 3}
    },
    {
      "action": "publish_service",
      "result": {"service": "contracts/entity"}
    },
    {
      "action": "attach_schema_bundle",
      "result": {"attached": true}
    }
  ],
  "service_path": "contracts/entity",
  "tests_generated": true,
  "correlation_id": "pqr-678"
}
```

## Use Case 7: Bulk Backfill & Regression

**Description**: Execute large-scale data processing with validation.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase7/bulk-backfill \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "data_source": "s3://bucket/historical-trades/",
    "window_size": 1000,
    "target_model": "Trade",
    "validate_sample": true
  }'
```

### Response

```json
{
  "use_case": "bulk_backfill",
  "status": "completed",
  "results": [
    {
      "action": "plan_ingestion",
      "result": {
        "total_records": 1000000,
        "windows": 1000
      }
    },
    {
      "action": "validate_sample",
      "result": {"sample_valid": true}
    },
    {
      "action": "execute_backfill",
      "result": {
        "processed": 1000000,
        "failed": 0,
        "duration_seconds": 3600
      }
    },
    {
      "action": "record_manifest",
      "result": {
        "manifest_id": "backfill-20240101",
        "location": "artifacts/manifest.json"
      }
    }
  ],
  "window_size": 1000,
  "sample_validated": true,
  "correlation_id": "stu-901"
}
```

## Use Case 8: Incident Response / Rollback

**Description**: Emergency rollback and recovery procedures.

### Request

```bash
curl -X POST http://localhost:8000/flows/usecase8/incident-rollback \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "service_path": "trades/byNotional",
    "target_version": null,
    "create_hotfix": true
  }'
```

### Response

```json
{
  "use_case": "incident_rollback",
  "status": "completed",
  "results": [
    {
      "action": "list_versions",
      "result": ["1.0.0", "1.0.1", "1.0.2", "1.1.0"]
    },
    {
      "action": "find_last_good_version",
      "result": {"version": "1.0.2", "status": "stable"}
    },
    {
      "action": "create_hotfix_workspace",
      "result": {"workspace": "hotfix-20240101"}
    },
    {
      "action": "revert_to_version",
      "result": {"reverted": true}
    },
    {
      "action": "compile",
      "result": {"status": "success"}
    },
    {
      "action": "flip_traffic",
      "result": {"traffic_switched": true}
    }
  ],
  "service_path": "trades/byNotional",
  "rolled_back_to": "1.0.2",
  "hotfix_created": true,
  "correlation_id": "vwx-234"
}
```

## Natural Language Interface

The agent also supports natural language intents:

### Example Request

```bash
curl -X POST http://localhost:8000/intent \
  -H "Authorization: Bearer demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Trade model with fields id, ticker, quantity, and price. Then compile it and generate a REST service at trades/all",
    "execute": true
  }'
```

### Example Response

```json
{
  "correlation_id": "xyz-567",
  "prompt": "Create a Trade model...",
  "plan": [
    {
      "id": "step_0",
      "action": "create_model",
      "params": {"name": "Trade"},
      "status": "completed"
    },
    {
      "id": "step_1",
      "action": "compile",
      "params": {},
      "status": "completed"
    },
    {
      "id": "step_2",
      "action": "generate_service",
      "params": {"path": "trades/all"},
      "status": "completed"
    }
  ],
  "status": "completed",
  "execution_time_ms": 2341.5
}
```

## Error Handling

All endpoints return structured errors:

```json
{
  "code": "COMPILATION_ERROR",
  "message": "Failed to compile PURE code",
  "hint": "Check PURE syntax at line 5",
  "correlation_id": "abc-123",
  "upstream_context": {
    "engine_error": "Unexpected token '}'"
  }
}
```

## Rate Limiting

- Default: 100 requests per minute per API key
- Burst: 10 requests per second
- Headers returned:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1704123600

## Authentication

All requests require Bearer token authentication:

```bash
curl -H "Authorization: Bearer your-api-key" ...
```

## Correlation IDs

All requests can include a correlation ID for tracing:

```bash
curl -H "X-Correlation-ID: my-trace-123" ...
```

The correlation ID is returned in responses and logged for debugging.