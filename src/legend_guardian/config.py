"""Application settings module."""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Legend Guardian Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = ["*"]

    # API Configuration
    api_key: str = Field(default="demo-key", description="Default API key")
    valid_api_keys: List[str] = Field(default_factory=lambda: ["demo-key"], description="Valid API keys")
    
    # Legend Services
    engine_url: str = Field(default="http://localhost:6300", description="Legend Engine URL")
    sdlc_url: str = Field(default="http://localhost:6100", description="Legend SDLC URL")
    depot_url: str = Field(default="http://localhost:6200", description="Legend Depot URL")
    studio_url: str = Field(default="http://localhost:9000", description="Legend Studio URL")
    
    # Service Tokens
    engine_token: Optional[str] = Field(default=None, description="Legend Engine auth token")
    sdlc_token: Optional[str] = Field(default=None, description="Legend SDLC auth token")
    depot_token: Optional[str] = Field(default=None, description="Legend Depot auth token")
    
    # Default Project Settings
    project_id: str = Field(default="demo-project", description="Default project ID")
    workspace_id: str = Field(default="terry-dev", description="Default workspace ID")
    service_path: str = Field(default="trades/byNotional", description="Default service path")
    
    # Database
    database_url: str = Field(
        default="postgresql://legend:legend@localhost:5432/legend",
        description="PostgreSQL connection string"
    )
    
    # MongoDB (for Legend services)
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection string"
    )
    
    # Redis (for caching)
    redis_url: Optional[str] = Field(default=None, description="Redis connection string")
    
    # OpenTelemetry
    otel_enabled: bool = Field(default=False, description="Enable OpenTelemetry")
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4317",
        description="OTLP endpoint"
    )
    otel_service_name: str = Field(default="legend-guardian-agent", description="Service name for traces")
    
    # Agent Configuration
    agent_model: str = Field(default="gpt-4", description="LLM model for agent")
    agent_temperature: float = Field(default=0.7, description="LLM temperature")
    agent_max_tokens: int = Field(default=2000, description="Max tokens for LLM responses")
    
    # RAG Configuration
    rag_enabled: bool = Field(default=True, description="Enable RAG for context")
    rag_chunk_size: int = Field(default=1000, description="Chunk size for document splitting")
    rag_chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    vector_store_type: str = Field(default="chroma", description="Vector store type (chroma/pgvector)")
    
    # Security
    pii_redaction_enabled: bool = Field(default=True, description="Enable PII redaction in logs")
    max_request_size: int = Field(default=10485760, description="Max request size in bytes (10MB)")
    
    # Performance
    request_timeout: int = Field(default=30, description="Default request timeout in seconds")
    max_retries: int = Field(default=3, description="Max retries for failed requests")
    circuit_breaker_threshold: int = Field(default=5, description="Circuit breaker failure threshold")
    
    @field_validator("valid_api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        """Parse comma-separated API keys."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()