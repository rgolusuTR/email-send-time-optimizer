import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # AEM Configuration
    aem_base_url: str = os.getenv("AEM_BASE_URL", "https://author-ppe-ams.ewp.thomsonreuters.com/sites.html/content")
    aem_username: str = os.getenv("AEM_USERNAME", "")
    aem_password: str = os.getenv("AEM_PASSWORD", "")
    
    # AI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Browser Configuration
    headless_mode: bool = os.getenv("HEADLESS_MODE", "false").lower() == "true"
    browser_timeout: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    class Config:
        env_file = ".env"

settings = Settings()
