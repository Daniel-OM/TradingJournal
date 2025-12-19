import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información de la app
    APP_NAME: str = "Trading Journal API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv(key="DEBUG", default="True").lower() == "true"
    ENVIRONMENT = os.getenv(key="ENVIRONMENT", default="development")
    
    # Base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./trading_journal.db"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv(key="SECRET_KEY", default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Upload folder
    UPLOAD_FOLDER: str = os.getenv(key="UPLOAD_FOLDER", default="./uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
