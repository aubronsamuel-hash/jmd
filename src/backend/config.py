from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application runtime configuration."""

    database_url: str = Field(
        default="sqlite+pysqlite:///./jmd.db",
        description="SQLAlchemy database URL.",
    )
    secret_key: str = Field(
        default="dev-secret",
        description="Secret used for token derivation.",
    )
    access_token_ttl_seconds: int = Field(default=3600, ge=60)
    magic_link_ttl_seconds: int = Field(default=900, ge=60)
    invitation_ttl_seconds: int = Field(default=3 * 24 * 3600, ge=3600)
    environment: Literal["dev", "test", "prod"] = Field(default="dev")

    model_config = {
        "env_prefix": "BACKEND_",
        "env_file": ".env",
        "extra": "ignore",
    }

    @field_validator("database_url")
    @classmethod
    def _strip(cls, value: str) -> str:  # noqa: D401
        """Normalise the database URL."""

        return value.strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings instance."""

    return Settings()
