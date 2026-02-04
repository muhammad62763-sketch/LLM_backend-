from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with Pydantic validation"""
    
    # Application
    APP_NAME: str = "Multi-API Chat Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    
    # Database (Neon PostgreSQL)
    DATABASE_URL: str = Field(..., description="Neon PostgreSQL connection string")
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # API Keys
    GROQ_API_KEY: str
    GOOGLE_SEARCH_API_KEY: str
    GEMINI_API_KEY: str
    CEREBRAS_API_KEY: str
    MISTRAL_API_KEY: str
    OPENROUTER_API_KEY: str
    HUGGINGFACE_API_KEY: str
    DEEPSEEK_API_KEY: str
    
    # Rate Limits
    GROQ_RPM: int = 30
    GROQ_TPM: int = 6000
    GROQ_TPD: int = 500000
    CEREBRAS_RPM: int = 60
    CEREBRAS_TPM: int = 10000
    CEREBRAS_TPD: int = 1000000
    OPENROUTER_RPM: int = 200
    OPENROUTER_TPM: int = 100000
    OPENROUTER_TPD: int = 10000000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL is for PostgreSQL"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v


settings = Settings()
