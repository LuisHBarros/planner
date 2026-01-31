"""Application configuration."""
import os


class Settings:
    """App settings loaded from environment."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./planner.db")
        self.jwt_secret = os.getenv("JWT_SECRET", "dev-secret")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.llm_api_url = os.getenv("LLM_API_URL")
        self.llm_api_key = os.getenv("LLM_API_KEY")


settings = Settings()
