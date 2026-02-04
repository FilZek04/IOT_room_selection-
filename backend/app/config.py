from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.

    Settings are loaded from environment variables or .env file.
    For local development, create a .env file in the backend/ directory.
    """

    # Application
    APP_NAME: str = "IoT Room Selection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "iot_room_selection"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # CORS - Allow frontend access
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5175",  # Vite dev server (alternate port)
        "http://172.20.10.2:5173",  # Pi network IP
    ]

    # Optional: JWT Authentication (for bonus feature)
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
