# app/core/config.py

import os
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",  # important for env safety
    )

    project_name: str = "Secure Multi-Tenant Backend"
    environment: str = "dev"
    log_level: str = "info"
    tenant_default_name: str = "default"

    database_url: str | None = None

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # === AUDIT SIGNING (SECURITY-GRADE) ===
    audit_signing_key: str

    @property
    def effective_database_url(self) -> str:
        env_db = os.getenv("DATABASE_URL")
        if env_db:
            return env_db

        if self.database_url:
            return self.database_url

        raise RuntimeError("DATABASE_URL is required")


settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
