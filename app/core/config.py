# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev")


class Settings(BaseSettings):
    project_name: str = "Secure Multi-Tenant Backend"

    database_url: str
    secret_key: str
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env.test" if ENV == "test" else ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
