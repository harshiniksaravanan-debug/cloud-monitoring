from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./monitoring.db"
    check_interval_seconds: int = 60
    request_timeout_seconds: int = 10
    incident_cooldown_minutes: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
