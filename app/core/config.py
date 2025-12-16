from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "Secure Multi-Tenant Backend"

    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"
    )

settings = Settings()
