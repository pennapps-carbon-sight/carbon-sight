#!/usr/bin/env python3
"""
Entry point for running the CarbonSight Dashboard API.
"""

import uvicorn
from config import config

if __name__ == "__main__":
    print("🌱 Starting CarbonSight Dashboard API...")
    print(f"🔧 Environment: {'Development' if config.debug else 'Production'}")
    print(f"🌐 Server: http://{config.host}:{config.port}")
    print(f"📚 API Docs: http://{config.host}:{config.port}/docs")
    print(f"🔄 Auto-reload: {config.debug}")
    
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info"
    )
