import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RetailFlow — Marketplace Fulfilment Recovery Agent"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "sqlite+aiosqlite:///./retailflow.db"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # mock, gemini, bedrock, openai
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Event Replay Engine
    REPLAY_INTERVAL_SECONDS: float = float(os.getenv("REPLAY_INTERVAL_SECONDS", "1.5"))
    AUTO_REPLAY_ON_START: bool = True
    RISK_THRESHOLD_SCORE: float = 0.65  # Triggers agent investigation pipeline
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
