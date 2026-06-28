from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://aqarix:aqarix@localhost:5432/aqarix"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_public_per_minute: int = 60
    rate_limit_user_per_minute: int = 120
    quota_writes_per_day: int = 1000
    quota_lead_rooms_per_day: int = 25
    cost_alert_requests_per_day: int = 1000
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    clerk_secret_key: str = ""
    sentry_dsn: str = ""
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "https://aqari-x.vercel.app,https://aqarix-production.up.railway.app"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
