import os
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Secure Multi-Tenant Backend"

    # Environment: dev / test / prod
    environment: str = "dev"

    # Logging
    log_level: str = "info"

    # Multi-tenant
    tenant_default_name: str = "default"

    # Base paths
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir: str = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    # Database
    database_url: str | None = None

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def effective_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        default_sqlite = f"sqlite:///{os.path.join(self.data_dir, 'secure_backend.db')}"
        if self.environment == "dev":
            return default_sqlite

        raise RuntimeError("DATABASE_URL is required in non-dev environments")


settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
