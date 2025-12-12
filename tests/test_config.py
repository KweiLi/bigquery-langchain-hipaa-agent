"""
Tests for configuration module.
"""

import pytest
from pydantic import ValidationError
from src.config.settings import Settings


class TestSettings:
    """Tests for Settings configuration."""
    
    def test_settings_loading(self, test_env):
        """Test settings load from environment."""
        settings = Settings()
        
        assert settings.gcp_project_id == "test-project"
        assert settings.gcp_dataset_id == "test-dataset"
        assert settings.environment == "test"
        assert settings.llm_model == "gpt-4"
    
    def test_is_production(self, test_env):
        """Test production environment detection."""
        settings = Settings()
        assert not settings.is_production
        
        # Test with production environment
        settings.environment = "production"
        assert settings.is_production
    
    def test_is_hipaa_compliant_config(self, test_env):
        """Test HIPAA compliance configuration check."""
        settings = Settings()
        assert settings.is_hipaa_compliant_config
        
        # Test with non-compliant config
        settings.enable_encryption = False
        assert not settings.is_hipaa_compliant_config
    
    def test_log_level_validation(self, test_env):
        """Test log level validation."""
        # Valid log level
        settings = Settings()
        settings.log_level = "DEBUG"
        assert settings.log_level == "DEBUG"
        
        # Invalid log level should raise error
        with pytest.raises(ValidationError):
            Settings(log_level="INVALID")
    
    def test_environment_validation(self, test_env):
        """Test environment validation."""
        settings = Settings()
        
        # Valid environments
        for env in ["development", "staging", "production"]:
            settings.environment = env
            assert settings.environment == env
        
        # Invalid environment should raise error during initialization
        with pytest.raises(ValidationError):
            Settings(environment="invalid")
    
    def test_rate_limiting_settings(self, test_env):
        """Test rate limiting configuration."""
        settings = Settings()
        
        assert settings.max_queries_per_minute == 10
        assert settings.max_queries_per_hour == 100
        assert settings.max_queries_per_minute > 0
        assert settings.max_queries_per_hour > 0
    
    def test_bigquery_settings(self, test_env):
        """Test BigQuery specific settings."""
        settings = Settings()
        
        assert settings.bigquery_max_results == 1000
        assert settings.bigquery_timeout_seconds == 300
        assert settings.enable_query_cache is True
    
    def test_phi_fields_default(self, test_env):
        """Test PHI fields default configuration."""
        settings = Settings()
        
        expected_phi_fields = [
            "patient_id", "ssn", "medical_record_number", "name", "dob"
        ]
        assert settings.phi_fields == expected_phi_fields
    
    def test_data_retention(self, test_env):
        """Test data retention settings for HIPAA."""
        settings = Settings()
        
        # HIPAA requires 7 years (approximately 2555 days)
        assert settings.data_retention_days == 2555
