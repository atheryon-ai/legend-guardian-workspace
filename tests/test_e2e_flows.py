import os
import sys
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

# Ensure `src` is on sys.path for direct imports (matches pattern in existing tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from legend_guardian.api.main import app  # type: ignore


class DummyOrchestrator:
    """Lightweight stub to avoid external Legend service calls."""

    def __init__(self, settings):
        self.settings = settings

    async def execute_step(self, action: str, params: Dict[str, Any]):
        # Return a deterministic structure per action
        return {"ok": True, "action": action, "params": params}


@pytest.fixture(autouse=True)
def _patch_orchestrator(monkeypatch):
    # Patch the orchestrator used by flows router to the dummy stub
    import legend_guardian.api.routers.flows as flows_router

    monkeypatch.setattr(flows_router, "AgentOrchestrator", DummyOrchestrator)


@pytest.fixture()
def client():
    return TestClient(app)


def _auth_headers(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"Authorization": "Bearer demo-key"}
    if extra:
        headers.update(extra)
    return headers


def test_auth_required_on_flows(client: TestClient):
    # Missing Authorization should yield 401
    resp = client.post("/flows/usecase7/bulk-backfill", json={})
    assert resp.status_code == 401


def test_usecase1_ingest_publish(client: TestClient):
    payload = {
        "csv_data": "id,ticker,qty,price\n1,AAPL,10,180.5",
        "model_name": "Trade",
        "service_path": "trades/byTicker",
        "mapping_name": "TradeFlatDataMapping",
    }
    resp = client.post("/flows/usecase1/ingest-publish", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "ingest_publish"
    assert body["status"] == "completed"
    # Steps: create_workspace, create_model, create_mapping, compile, generate_service, open_review
    assert len(body["results"]) == 6
    assert "service_url" in body
    assert "correlation_id" in body


def test_usecase2_safe_rollout(client: TestClient):
    payload = {
        "model_path": "model::Trade",
        "changes": {"add_property": {"name": "desk", "type": "String"}},
        "keep_v1": True,
    }
    resp = client.post("/flows/usecase2/safe-rollout", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "safe_rollout"
    assert body["status"] == "completed"
    # Steps: create_workspace, apply_changes, compile, run_tests, create_v2_service, open_review
    assert len(body["results"]) == 6
    assert body["v1_maintained"] is True


def test_usecase3_model_reuse(client: TestClient):
    payload = {
        "search_query": "instrument schema",
        "target_format": "avro",
        "service_name": "InstrumentService",
    }
    resp = client.post("/flows/usecase3/model-reuse", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "model_reuse"
    assert body["status"] == "completed"
    # Steps: search_depot, import_model, transform_schema, create_service
    assert len(body["results"]) == 4
    assert body["schema_format"] == "avro"


def test_usecase4_reverse_etl(client: TestClient):
    payload = {
        "source_table": "public.trades",
        "model_name": "TradeModel",
        "constraints": ["quantity > 0"],
    }
    resp = client.post("/flows/usecase4/reverse-etl", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "reverse_etl"
    assert body["status"] == "completed"
    # Steps: analyze_table, generate_model, add_constraints, compile, create_data_product, export_schema
    assert len(body["results"]) == 6
    assert body["model_created"] == "TradeModel"


def test_usecase5_governance_audit(client: TestClient):
    payload = {
        "scope": "all",
        "include_tests": True,
        "generate_evidence": True,
    }
    resp = client.post("/flows/usecase5/governance-audit", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "governance_audit"
    assert body["status"] == "completed"
    # Steps: enumerate_entities, compile_all, run_constraint_tests, generate_evidence_bundle
    assert len(body["results"]) == 4
    assert body["evidence_generated"] is True


def test_usecase6_contract_first(client: TestClient):
    payload = {
        "schema": {"title": "Trade", "type": "object", "properties": {"id": {"type": "string"}}},
        "service_path": "contract/trades",
        "generate_tests": True,
    }
    resp = client.post("/flows/usecase6/contract-first", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "contract_first"
    assert body["status"] == "completed"
    # Steps: schema_to_model, compile, generate_positive_tests, generate_negative_tests, publish_service, attach_schema_bundle
    assert len(body["results"]) == 6
    assert body["tests_generated"] is True


def test_usecase7_bulk_backfill(client: TestClient):
    payload = {
        "data_source": "s3://bucket/path",
        "window_size": 500,
        "target_model": "TradeModel",
        "validate_sample": True,
    }
    resp = client.post("/flows/usecase7/bulk-backfill", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "bulk_backfill"
    assert body["status"] == "completed"
    # Steps: plan_ingestion, validate_sample, execute_backfill, record_manifest
    assert len(body["results"]) == 4
    assert body["sample_validated"] is True


def test_usecase8_incident_rollback(client: TestClient):
    payload = {
        "service_path": "trades/byTicker",
        # omit target_version to trigger discovery
        "target_version": None,
        "create_hotfix": True,
    }
    resp = client.post("/flows/usecase8/incident-rollback", headers=_auth_headers(), json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["use_case"] == "incident_rollback"
    assert body["status"] == "completed"
    # Steps: list_versions, find_last_good_version, create_hotfix_workspace, revert_to_version, compile, flip_traffic
    assert len(body["results"]) == 6
    assert body["hotfix_created"] is True


def test_correlation_id_roundtrip(client: TestClient):
    payload = {
        "csv_data": "id,ticker\n1,AAPL",
        "model_name": "Trade",
        "service_path": "trades/byTicker",
    }
    corr = "test-corr-id-123"
    resp = client.post(
        "/flows/usecase1/ingest-publish",
        headers=_auth_headers({"X-Correlation-ID": corr}),
        json=payload,
    )
    assert resp.status_code == 200
    assert resp.json().get("correlation_id") == corr
