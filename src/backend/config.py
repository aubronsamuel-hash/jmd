"""Application configuration utilities."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = Field(default="JMD Planning API", alias="BACKEND_APP_NAME")
    environment: str = Field(default="development", alias="BACKEND_ENV")
    api_prefix: str = Field(default="/api/v1", alias="BACKEND_API_PREFIX")

    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
