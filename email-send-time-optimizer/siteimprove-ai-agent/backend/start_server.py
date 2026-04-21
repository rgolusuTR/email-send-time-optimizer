"""
Startup script for Siteimprove AI Agent backend server
"""
import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    print("🚀 Starting Siteimprove AI Agent Backend Server...")
    print(f"📍 Server will run on: http://{settings.host}:{settings.port}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🌐 CORS origins: {settings.cors_origins}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
