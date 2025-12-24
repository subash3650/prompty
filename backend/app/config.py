"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file with validation.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All values are read from:
    1. Environment variables (highest priority)
    2. .env file in backend root directory
    3. Default values defined here (lowest priority)
    """
    
    # ===========================================
    # DATABASE
    # ===========================================
    database_url: str = ""  # REQUIRED - Set in .env
    
    # ===========================================
    # JWT AUTHENTICATION
    # ===========================================
    jwt_secret: str = ""  # REQUIRED - Set in .env
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 6
    
    # ===========================================
    # GROQ AI API
    # ===========================================
    groq_api_key: str = ""  # REQUIRED - Set in .env
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30
    
    # ===========================================
    # CORS CONFIGURATION
    # ===========================================
    cors_origins: str = "http://localhost:3000"
    
    # ===========================================
    # SERVER CONFIGURATION
    # ===========================================
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # ===========================================
    # RATE LIMITING
    # ===========================================
    rate_limit_per_minute: int = 10
    
    # ===========================================
    # EVENT CONFIGURATION
    # ===========================================
    event_name: str = "Prompty Challenge"
    max_concurrent_users: int = 60
    
    # ===========================================
    # ADMIN CONFIGURATION
    # ===========================================
    admin_username: str = "admin"
    admin_password: str = ""  # REQUIRED - Set in .env
    
    # ===========================================
    # LOGGING
    # ===========================================
    log_level: str = "INFO"
    
    # ===========================================
    # PYDANTIC SETTINGS CONFIGURATION
    # ===========================================
    model_config = SettingsConfigDict(
        env_file=".env",           # Load from .env file
        env_file_encoding="utf-8",
        case_sensitive=False,       # DATABASE_URL and database_url both work
        extra="ignore",             # Ignore extra env vars
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid re-reading .env on every call.
    """
    return Settings()


# Singleton instance for direct imports
settings = get_settings()
