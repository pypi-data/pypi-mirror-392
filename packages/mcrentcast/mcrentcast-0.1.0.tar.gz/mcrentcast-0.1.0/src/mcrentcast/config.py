"""Configuration management for mcrentcast MCP server."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from .env file
    )
    
    # Environment
    mode: str = Field(default="development", description="Application mode")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Rentcast API
    rentcast_api_key: Optional[str] = Field(default=None, description="Rentcast API key")
    rentcast_base_url: str = Field(default="https://api.rentcast.io/v1", description="Rentcast API base URL")
    
    # Mock API Settings
    use_mock_api: bool = Field(default=False, description="Use mock API for testing")
    mock_api_url: str = Field(default="http://mock-rentcast-api:8001/v1", description="Mock API URL")
    
    # Rate Limiting
    daily_api_limit: int = Field(default=100, description="Daily API request limit")
    monthly_api_limit: int = Field(default=1000, description="Monthly API request limit") 
    requests_per_minute: int = Field(default=3, description="Requests per minute limit")
    
    # Cache Settings
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")
    max_cache_size_mb: int = Field(default=100, description="Maximum cache size in MB")
    
    # Database
    database_url: str = Field(default="sqlite:///./data/mcrentcast.db", description="Database URL")
    
    # MCP Server
    mcp_server_port: int = Field(default=3001, description="MCP server port")
    
    # Paths
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    cache_dir: Path = Field(default=Path("./data/cache"), description="Cache directory")
    
    # Security
    confirmation_timeout_minutes: int = Field(default=15, description="User confirmation timeout in minutes")
    exponential_backoff_base: float = Field(default=2.0, description="Exponential backoff base")
    exponential_backoff_max_delay: int = Field(default=300, description="Max delay for exponential backoff in seconds")
        
    def __init__(self, **data):
        super().__init__(**data)
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.mode == "development"
        
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.mode == "production"
        
    def validate_api_key(self) -> bool:
        """Validate that API key is configured."""
        return bool(self.rentcast_api_key and self.rentcast_api_key.strip())


# Global settings instance
settings = Settings()