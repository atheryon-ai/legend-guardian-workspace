#!/usr/bin/env python3
"""
Configuration Settings

Configuration management for the Legend Guardian Agent system.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Legend Platform Configuration
    legend_engine_url: str = Field(
        default="http://52.186.106.13:6060",
        description="Legend Engine service URL (Azure)"
    )
    legend_sdlc_url: str = Field(
        default="http://52.186.106.13:7070", 
        description="Legend SDLC service URL (Azure)"
    )
    legend_api_key: Optional[str] = Field(
        default=None,
        description="Legend platform API key"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_debug: bool = Field(default=False, description="API debug mode")
    
    # Security Configuration
    valid_api_keys: str = Field(
        default="",
        description="Comma-separated list of valid API keys"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Memory Configuration
    max_memory_entries: int = Field(
        default=1000,
        description="Maximum number of memory entries to keep"
    )
    
    class Config:
        env_prefix = "LEGEND_"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
