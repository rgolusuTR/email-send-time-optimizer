"""
Configuration settings for Siteimprove AI Agent
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Siteimprove Credentials
    siteimprove_username: str = os.getenv("SITEIMPROVE_USERNAME", "")
    siteimprove_password: str = os.getenv("SITEIMPROVE_PASSWORD", "")
    
    # Application Settings
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Browser Settings
    headless_mode: bool = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    browser_timeout: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    screenshot_path: str = os.getenv("SCREENSHOT_PATH", "./screenshots")
    
    # Data Settings
    cache_duration: int = int(os.getenv("CACHE_DURATION", "300"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # API Settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Siteimprove URLs
    siteimprove_base_url: str = "https://www.siteimprove.com/"
    siteimprove_login_url: str = "https://identity.siteimprove.com/"
    siteimprove_dashboard_url: str = "https://my2.siteimprove.com/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
