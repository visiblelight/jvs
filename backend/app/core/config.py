from pydantic_settings import BaseSettings
from pydantic import field_validator
from zoneinfo import ZoneInfo


class Settings(BaseSettings):
    PROJECT_NAME: str = "JVS"
    VERSION: str = "0.1.0"
    BUSINESS_TIMEZONE: str = "Asia/Shanghai"

    @field_validator("BUSINESS_TIMEZONE")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except (KeyError, ValueError) as exc:
            raise ValueError("BUSINESS_TIMEZONE 必须是有效的 IANA 时区") from exc
        return value

    # Database — switch to PostgreSQL by changing DATABASE_URL in .env
    DATABASE_URL: str = "sqlite:///./dev.db"

    # Redis (reserved for future use)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3001,http://localhost:3002"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = {"env_file": ".env"}


settings = Settings()
