from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Secure Multi-Tenant Backend"
    database_url: str = "sqlite:///./secure_backend.db"
    secret_key: str = "super-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
