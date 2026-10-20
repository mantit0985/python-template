from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Python Template Service"
    ENVIRONMENT: str = "development"
    API_VERSION: str = "0.1.0"

    # Security
    CORS_ORIGINS: list[str] = []

    # Observability
    LOG_LEVEL: str = "INFO"

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/5m"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
