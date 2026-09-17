import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RetailFlow — Marketplace Fulfilment Recovery Agent"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = "sqlite+aiosqlite:///./retailflow.db"
    
    # AWS Bedrock is the only cloud demo provider. A deterministic fallback is
    # explicit in status responses when Bedrock is unavailable.
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "bedrock")
    BEDROCK_MODEL: str = os.getenv("BEDROCK_MODEL", "us.amazon.nova-lite-v1:0")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE: Optional[str] = os.getenv("AWS_PROFILE") or None
    BEDROCK_ALLOWED_MODELS: str = os.getenv(
        "BEDROCK_ALLOWED_MODELS",
        "us.amazon.nova-lite-v1:0,us.amazon.nova-pro-v1:0",
    )
    
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
    
    # Event Replay Engine
    REPLAY_INTERVAL_SECONDS: float = float(os.getenv("REPLAY_INTERVAL_SECONDS", "1.5"))
    AUTO_REPLAY_ON_START: bool = False
    RISK_THRESHOLD_SCORE: float = 0.65  # Triggers agent investigation pipeline
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
