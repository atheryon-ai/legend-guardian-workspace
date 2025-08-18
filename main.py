#!/usr/bin/env python3
"""
Legend Guardian Agent - Main Entry Point

Main entry point for running the Legend Guardian Agent API service.
"""

import uvicorn
from src.api.main import app

if __name__ == "__main__":
    # Run the API service
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
