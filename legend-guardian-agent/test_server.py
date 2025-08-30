#!/usr/bin/env python3
"""Simple test server to demonstrate the Legend Guardian Agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import httpx

app = FastAPI(title="Legend Guardian Agent Test", version="1.0.0")

# Mock Legend service URLs
ENGINE_URL = "http://localhost:6300"
SDLC_URL = "http://localhost:6100"
DEPOT_URL = "http://localhost:6200"


class CompileRequest(BaseModel):
    """PURE compilation request."""
    pure: str


class IntentRequest(BaseModel):
    """Intent request."""
    prompt: str
    execute: bool = True


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Legend Guardian Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    services = {}
    
    # Check Legend services (mock for now if they're not running)
    for name, url in [("engine", ENGINE_URL), ("sdlc", SDLC_URL), ("depot", DEPOT_URL)]:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{url}/api/info", follow_redirects=True)
                services[name] = {"status": "up" if response.status_code < 500 else "down"}
        except:
            services[name] = {"status": "down", "error": "Connection failed"}
    
    # Determine overall status
    all_down = all(s.get("status") == "down" for s in services.values())
    
    return {
        "status": "ok" if not all_down else "degraded",
        "version": "1.0.0",
        "services": services,
        "message": "Legend Guardian Agent is operational"
    }


@app.post("/adapters/engine/compile")
async def compile_pure(request: CompileRequest):
    """Compile PURE code."""
    # Mock compilation for demonstration
    pure_code = request.pure.lower()
    
    if "class" in pure_code:
        return {
            "ok": True,
            "details": {
                "status": "SUCCESS",
                "message": "PURE code compiled successfully",
                "classes": 1
            }
        }
    else:
        return {
            "ok": False,
            "errors": [
                {"line": 1, "message": "Expected 'Class' keyword"}
            ]
        }


@app.post("/intent")
async def process_intent(request: IntentRequest):
    """Process natural language intent."""
    prompt = request.prompt.lower()
    
    # Simple intent parsing
    steps = []
    
    if "create" in prompt and "model" in prompt:
        steps.append({
            "action": "create_model",
            "status": "completed" if request.execute else "planned"
        })
    
    if "compile" in prompt:
        steps.append({
            "action": "compile",
            "status": "completed" if request.execute else "planned"
        })
    
    if "service" in prompt:
        steps.append({
            "action": "generate_service",
            "status": "completed" if request.execute else "planned"
        })
    
    return {
        "prompt": request.prompt,
        "plan": steps,
        "status": "completed" if request.execute else "planned",
        "message": f"Processed {len(steps)} steps from intent"
    }


@app.get("/adapters/sdlc/projects")
async def list_projects():
    """List SDLC projects."""
    return [
        {"id": "demo-project", "name": "Demo Project"},
        {"id": "test-project", "name": "Test Project"}
    ]


@app.get("/adapters/depot/search")
async def search_depot(q: str = ""):
    """Search depot."""
    return [
        {"path": f"model::{q}", "type": "Class", "project": "demo"}
    ]


if __name__ == "__main__":
    import uvicorn
    print("Starting Legend Guardian Agent Test Server...")
    print("Access the API at: http://localhost:8002")
    print("Interactive docs at: http://localhost:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)