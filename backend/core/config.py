from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application core configuration settings.
    
    Loads configuration from environment variables and an optional .env file.
    Provides typed configuration fields with sensible defaults for development.
    """
    
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # Security
    SECRET_KEY: str = "super-secret-default-key-please-change-in-production"
    
    # Database
    DATABASE_URL: str
    
    # API Keys & 3rd Party Services
    GEMINI_API_KEY: str
    RESEND_API_KEY: str | None = None
    FIREBASE_CREDENTIALS_PATH: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def is_production(self) -> bool:
        """Helper property to check if running in production environment."""
        return self.ENVIRONMENT == "production"
        
    @property
    def is_development(self) -> bool:
        """Helper property to check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Export a singleton settings instance
settings = Settings()
