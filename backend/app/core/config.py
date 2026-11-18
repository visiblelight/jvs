from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from zoneinfo import ZoneInfo
from typing import Literal


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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, ge=1)
    REFRESH_IDLE_DAYS: int = Field(default=30, ge=1)
    REFRESH_ABSOLUTE_DAYS: int = Field(default=90, ge=1)
    REFRESH_COOKIE_SECURE: bool = True
    REFRESH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    @model_validator(mode="after")
    def valid_session_settings(self):
        if self.REFRESH_IDLE_DAYS > self.REFRESH_ABSOLUTE_DAYS:
            raise ValueError("REFRESH_IDLE_DAYS 不能大于 REFRESH_ABSOLUTE_DAYS")
        if self.REFRESH_COOKIE_SAMESITE == "none" and not self.REFRESH_COOKIE_SECURE:
            raise ValueError("SameSite=None 必须启用 Secure Cookie")
        return self

    model_config = {"env_file": ".env"}


settings = Settings()
