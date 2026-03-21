from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "JVS"
    VERSION: str = "0.1.0"

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
