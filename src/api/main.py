from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from src.api.routers import health, intent, adapters_engine

app = FastAPI(
    title="Legend Guardian Agent",
    description="An agent to interact with the FINOS Legend stack.",
    version="0.1.0",
)

app.include_router(health.router, tags=["Health"])
app.include_router(intent.router, prefix="/api", tags=["Intent"])

# Routers for future implementation
# from .routers import adapters_sdlc, adapters_depot, flows, webhooks
app.include_router(adapters_engine.router, prefix="/api", tags=["Engine Adapter"])
# app.include_router(adapters_sdlc.router)
# app.include_router(adapters_depot.router)
# app.include_router(flows.router)
# app.include_router(webhooks.router)

# Mount static GUI assets
app.mount(
    "/gui/static",
    StaticFiles(directory="src/web/static"),
    name="gui-static",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Legend Guardian Agent"}


@app.get("/gui")
def serve_gui():
    """Serve the minimal HTML GUI."""
    return FileResponse("src/web/static/index.html")
