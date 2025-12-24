"""
Configuration management using Pydantic Settings.
Loads environment variables with validation and defaults.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database (PostgreSQL with pg8000 driver) - MUST be set in .env
    database_url: str = ""
    
    # JWT - MUST be set in .env
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 6
    
    # Groq API
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    
    # Event
    event_name: str = "Prompty Challenge"
    max_concurrent_users: int = 60
    
    # Admin - MUST be set in .env
    admin_username: str = "admin"
    admin_password: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
