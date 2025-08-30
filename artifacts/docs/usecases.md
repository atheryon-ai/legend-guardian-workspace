
# Use Cases

This document describes the use cases supported by the Legend Guardian Agent.

## Use Case 1: Ingest -> Model -> Map -> Publish Service

**Description**: This use case covers the end-to-end flow of ingesting data, modeling it, mapping it, and publishing a service.

**Example**:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{ \
    "prompt": "ingest fx_options.csv -> CDM.Trade; compile; open PR; publish byNotional service", \
    "projectId": "demo-project", \
    "workspaceId": "terry-dev-uc1" \
  }' \
  http://localhost:8000/api/intent
```

**Expected Response**:

A JSON object containing the plan, actions, logs, and artifacts for the execution.

## Use Case 2: Model Change with Safe Rollout

(To be implemented)

## Use Case 3: Cross-bank Model Reuse via Depot

(To be implemented)

## Use Case 4: Reverse ETL -> Data Product

(To be implemented)

## Use Case 5: Governance Audit & Lineage Proof

(To be implemented)

## Use Case 6: Contract-first API

(To be implemented)

## Use Case 7: Bulk Backfill & Regression

(To be implemented)

## Use Case 8: Incident Response / Rollback

(To be implemented)
