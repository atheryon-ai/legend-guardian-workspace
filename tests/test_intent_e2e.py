
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_intent_e2e_use_case_1():
    payload = {
        "prompt": "ingest fx_options.csv -> CDM.Trade; compile; open PR; publish byNotional service",
        "projectId": "demo-project",
        "workspaceId": "terry-dev-e2e"
    }
    
    headers = {"X-API-Key": "demo-key"}
    
    response = client.post("/api/intent", json=payload, headers=headers)
    
    assert response.status_code == 200
    
    response_json = response.json()
    
    assert "plan" in response_json
    assert "actions" in response_json
    assert "logs" in response_json
    assert "artifacts" in response_json
    
    assert len(response_json["plan"]) == 5
    assert response_json["plan"][0]["action"] == "sdlc.create_workspace"
    assert response_json["plan"][1]["action"] == "sdlc.upsert_entities"
    assert response_json["plan"][2]["action"] == "engine.compile"
    assert response_json["plan"][3]["action"] == "sdlc.open_review"
    assert response_json["plan"][4]["action"] == "engine.run_service"
