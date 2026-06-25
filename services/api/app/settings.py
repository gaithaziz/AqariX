from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://aqarix:aqarix@localhost:5432/aqarix"
    redis_url: str = "redis://localhost:6379/0"
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    clerk_secret_key: str = ""
    sentry_dsn: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
