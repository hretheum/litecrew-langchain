#!/usr/bin/env python3
"""
LiteCrew API Server Runner
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from litecrew.api import create_app
from litecrew.config import Config

def main():
    """Run the LiteCrew API server."""
    # Validate configuration
    try:
        Config.validate()
        print(f"🚀 Starting LiteCrew API in {Config.ENVIRONMENT} mode...")
        print(f"📡 Available LLM providers: {', '.join(Config.get_available_providers()) or 'None configured'}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Create FastAPI app
    app = create_app()
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = Config.ENVIRONMENT == "development"
    
    # Log level
    log_level = "debug" if Config.DEBUG else "info"
    
    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
        # SSL options for production
        # ssl_keyfile="/path/to/key.pem",
        # ssl_certfile="/path/to/cert.pem",
    )


if __name__ == "__main__":
    main()