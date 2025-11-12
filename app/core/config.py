"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    For production, set these in your .env file or environment
    """

    # Application
    APP_NAME: str = "PyQuest"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    # Default to SQLite for local development
    # For PostgreSQL, use: postgresql://user:password@localhost/dbname
    DATABASE_URL: str = "sqlite:///./pyquest.db"

    # Security & Authentication
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Generate random key if not set
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Gamification
    XP_PER_CHALLENGE_BASE: int = 10
    XP_MULTIPLIER_INTERMEDIATE: float = 1.5
    XP_MULTIPLIER_ADVANCED: float = 2.0
    XP_MULTIPLIER_EXPERT: float = 3.0

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
