import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load environment variables from .env file, but don't fail if it doesn't exist
env_path = Path(".") / ".env"
if env_path.exists():
    logger.info(f"Loading environment from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.info("No .env file found, using environment variables")

class Settings:
    PROJECT_NAME: str = "NL2SQL Application"
    PROJECT_VERSION: str = "0.1.0"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    USE_LOCAL_AI: bool = os.getenv("USE_LOCAL_AI", "false").lower() == "true"
    LOCAL_AI_BASE_URL: str = os.getenv("LOCAL_AI_BASE_URL", "http://localhost:8080/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    logger.info(f"Using database URL: {DATABASE_URL}")
    
    # App Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")

settings = Settings()
logger.info(f"Using {'LocalAI' if settings.USE_LOCAL_AI else 'OpenAI'} for LLM services")
