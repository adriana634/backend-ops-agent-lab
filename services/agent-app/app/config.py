from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LAB_",
        extra="ignore",
    )

    app_name: str = "backend-ops-agent-lab"
    ollama_base_url: str = "http://ollama:11434/api"
    ollama_model: str = "qwen2:0.5b"
    mock_api_base_url: str = "http://mock-api:8001"
    qdrant_url: str = "http://qdrant:6333"

@lru_cache
def get_settings() -> Settings:
    return Settings()
