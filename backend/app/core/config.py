from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MindTrace API"
    app_env: str = "dev"
    app_debug: bool = True
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/mindtrace"
    )
    openai_api_key: str
    openai_base_url: str | None = None
    openai_default_model: str = "gpt-5.4-mini"

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
