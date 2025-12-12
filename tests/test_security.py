"""
Tests for HIPAA compliance and security features.
"""

import pytest
from src.security.hipaa_compliance import (
    EncryptionService,
    AuditLogger,
    AccessControl
)


class TestEncryptionService:
    """Tests for EncryptionService."""
    
    def test_encryption_decryption(self):
        """Test basic encryption and decryption."""
        service = EncryptionService("test-key-for-encryption-32b!")
        
        original_data = "sensitive patient information"
        encrypted = service.encrypt(original_data)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == original_data
        assert encrypted != original_data
    
    def test_empty_string_encryption(self):
        """Test encryption of empty string."""
        service = EncryptionService("test-key-for-encryption-32b!")
        
        encrypted = service.encrypt("")
        assert encrypted == ""
        
        decrypted = service.decrypt("")
        assert decrypted == ""
    
    def test_hash_phi(self):
        """Test PHI hashing for indexing."""
        service = EncryptionService("test-key-for-encryption-32b!")
        
        phi_value = "123-45-6789"
        hash1 = service.hash_phi(phi_value)
        hash2 = service.hash_phi(phi_value)
        
        # Same input should produce same hash
        assert hash1 == hash2
        
        # Hash should be different from original
        assert hash1 != phi_value
        
        # Hash should be hexadecimal
        assert all(c in '0123456789abcdef' for c in hash1)
    
    def test_invalid_decryption(self):
        """Test handling of invalid encrypted data."""
        service = EncryptionService("test-key-for-encryption-32b!")
        
        with pytest.raises(ValueError):
            service.decrypt("invalid-encrypted-data")


class TestAuditLogger:
    """Tests for AuditLogger."""
    
    def test_log_access(self):
        """Test access logging."""
        logger = AuditLogger()
        
        # Should not raise exception
        logger.log_access(
            user_id="test_user",
            action="READ",
            resource="patient_records",
            result="SUCCESS",
            phi_accessed=True
        )
    
    def test_log_query(self):
        """Test query logging."""
        logger = AuditLogger()
        
        logger.log_query(
            user_id="test_user",
            query="SELECT * FROM patients",
            query_hash="abc123",
            result_count=10,
            execution_time_ms=150.5,
            phi_fields_accessed=["name", "ssn"]
        )
    
    def test_log_phi_access(self):
        """Test PHI access logging."""
        logger = AuditLogger()
        
        logger.log_phi_access(
            user_id="test_user",
            record_id="patient_123",
            fields_accessed=["name", "ssn", "diagnosis"],
            purpose="treatment"
        )


class TestAccessControl:
    """Tests for AccessControl."""
    
    def test_check_phi_access_admin(self):
        """Test PHI access for admin role."""
        result = AccessControl.check_phi_access(
            user_role="admin",
            requested_fields=["name", "ssn", "diagnosis"]
        )
        assert result is True
    
    def test_check_phi_access_healthcare_provider(self):
        """Test PHI access for healthcare provider role."""
        result = AccessControl.check_phi_access(
            user_role="healthcare_provider",
            requested_fields=["name", "ssn"]
        )
        assert result is True
    
    def test_check_phi_access_analyst_denied(self):
        """Test PHI access denied for analyst role."""
        result = AccessControl.check_phi_access(
            user_role="analyst",
            requested_fields=["name", "ssn"]
        )
        assert result is False
    
    def test_check_phi_access_no_phi_requested(self):
        """Test access when no PHI is requested."""
        result = AccessControl.check_phi_access(
            user_role="analyst",
            requested_fields=["count", "avg_age"]
        )
        assert result is True
    
    def test_sanitize_query(self):
        """Test query sanitization."""
        query = "SELECT name, ssn FROM patients WHERE patient_id = 123"
        sanitized = AccessControl.sanitize_query(query)
        
        # PHI fields should be replaced
        assert "[PHI_FIELD]" in sanitized
        assert "name" not in sanitized or "name" == "[PHI_FIELD]"
