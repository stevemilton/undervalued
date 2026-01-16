"""Configuration module using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me-in-production"

    # Database
    database_url: str = "postgresql+psycopg://undervalued:undervalued@localhost:5432/undervalued"
    database_pool_size: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # External Services
    hmlr_sparql_endpoint: str = "https://landregistry.data.gov.uk/landregistry/query"
    epc_api_key: str = ""
    epc_api_url: str = "https://epc.opendatacommunities.org/api/v1"

    # Scraping
    scraper_rate_limit: int = 2
    scraper_headless: bool = True

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
