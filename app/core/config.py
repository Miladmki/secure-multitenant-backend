from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Secure Multi-Tenant Backend"

    database_url: str = "sqlite:///./secure_backend.db"

    secret_key: str = "super-secret-key-change-me"
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


settings = Settings()

# تعریف جداگانه برای OAuth2PasswordBearer (بیرون از کلاس Settings)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
