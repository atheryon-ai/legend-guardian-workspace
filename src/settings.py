
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENGINE_URL: str = "http://localhost:6300"
    SDLC_URL: str = "http://localhost:6100"
    DEPOT_URL: str = "http://localhost:6200"
    STUDIO_URL: str = "http://localhost:9000"
    AGENT_URL: str = "http://localhost:8000"
    API_KEY: str = "demo-key"
    PROJECT_ID: str = "demo-project"
    WORKSPACE_ID: str = "terry-dev"
    SERVICE_PATH: str = "trades/byNotional"
    
    VALID_API_KEYS: List[str] = ["demo-key"]
    
    ENGINE_TOKEN: str = "engine-token"
    SDLC_TOKEN: str = "sdlc-token"
    DEPOT_TOKEN: str = "depot-token"

    class Config:
        env_file = ".env"


settings = Settings()
