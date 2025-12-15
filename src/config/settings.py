"""
Configuration management module for the BigQuery LangChain Agent.
Implements secure configuration loading with environment variable validation.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with HIPAA compliance configurations."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Google Cloud Configuration
    gcp_project_id: str = Field(..., description="Google Cloud Project ID")
    gcp_dataset_id: str = Field(..., description="BigQuery Dataset ID")
    gcp_location: str = Field(default="US", description="BigQuery data location")
    google_application_credentials: str = Field(
        ..., description="Path to service account credentials"
    )
    
    # Vertex AI Configuration (replaces OpenAI)
    google_api_key: str = Field(..., description="Google AI API key")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model to use")

    # LLM Configuration
    openai_api_key: Optional[str] = Field(
        default=None, 
        description="OpenAI API key (not needed if using Vertex AI)"
    )
    llm_model: str = Field(default="gpt-4", description="LLM model to use")
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    
    # Security Configuration
    encryption_key: str = Field(..., description="Encryption key for sensitive data")
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, gt=0)
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    enable_audit_log: bool = Field(default=True)
    audit_log_bucket: Optional[str] = Field(default=None)
    
    # Application Configuration
    environment: str = Field(default="development")
    app_name: str = Field(default="BigQuery-LangChain-Agent")
    app_version: str = Field(default="1.0.0")
    api_port: int = Field(default=8000, gt=0, lt=65536)
    
    # HIPAA Compliance Settings
    enable_encryption: bool = Field(default=True)
    enable_audit_trail: bool = Field(default=True)
    data_retention_days: int = Field(default=2555, description="7 years for HIPAA")
    phi_fields: List[str] = Field(
        default_factory=lambda: [
            "patient_id", "ssn", "medical_record_number", "name", "dob"
        ]
    )
    
    # Rate Limiting
    max_queries_per_minute: int = Field(default=10, gt=0)
    max_queries_per_hour: int = Field(default=100, gt=0)
    
    # BigQuery Specific
    bigquery_max_results: int = Field(default=1000, gt=0)
    bigquery_timeout_seconds: int = Field(default=300, gt=0)
    enable_query_cache: bool = Field(default=True)
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_hipaa_compliant_config(self) -> bool:
        """Verify HIPAA compliance requirements are enabled."""
        return (
            self.enable_encryption
            and self.enable_audit_trail
            and self.enable_audit_log
        )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
