#!/usr/bin/env python3
"""
Run script for DataIntel Hub Backend - FastAPI Server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("NODE_ENV", "development") == "development"
    
    print(f"🚀 Starting DataIntel Hub Backend server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"📚 ReDoc Documentation: http://{host}:{port}/redoc")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 