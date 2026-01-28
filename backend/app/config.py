"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    # Use SQLite by default for local development/sample
    database_url: str = "sqlite:///./planner.db"
    
    # Environment
    env: str = "development"
    debug: bool = True
    
    # API
    api_title: str = "Planner API"
    api_version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
