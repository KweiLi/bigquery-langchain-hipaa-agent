"""
Security module implementing HIPAA compliance measures.
Includes encryption, audit logging, and access control utilities.
"""

import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


class EncryptionService:
    """Service for encrypting and decrypting sensitive data (PHI)."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service.
        
        Args:
            encryption_key: Base64 encoded encryption key. If None, uses settings.
        """
        key = encryption_key or settings.encryption_key
        
        # Ensure the key is properly formatted
        if not key:
            raise ValueError("Encryption key must be provided")
        
        try:
            # Try to use the key directly
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # If it fails, derive a proper key
            self.cipher = Fernet(self._derive_key(key))
    
    @staticmethod
    def _derive_key(password: str, salt: bytes = b'hipaa_salt_2024') -> bytes:
        """
        Derive a Fernet-compatible key from a password.
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation
            
        Returns:
            Base64 encoded 32-byte key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        if not data:
            return ""
        
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted plain text
        """
        if not encrypted_data:
            return ""
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise ValueError("Failed to decrypt data")
    
    def hash_phi(self, phi_value: str) -> str:
        """
        Create a one-way hash of PHI for indexing/searching.
        
        Args:
            phi_value: PHI value to hash
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(phi_value.encode()).hexdigest()


class AuditLogger:
    """Audit logger for HIPAA compliance tracking."""
    
    def __init__(self):
        """Initialize audit logger."""
        self.logger = structlog.get_logger("audit")
    
    def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        phi_accessed: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log access to resources for audit trail.
        
        Args:
            user_id: ID of user performing action
            action: Action performed (READ, WRITE, DELETE, etc.)
            resource: Resource accessed
            result: Result of action (SUCCESS, DENIED, ERROR)
            phi_accessed: Whether PHI was accessed
            metadata: Additional metadata
        """
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "phi_accessed": phi_accessed,
            "metadata": metadata or {},
            "event_type": "audit"
        }
        
        self.logger.info(
            "audit_log",
            **audit_entry
        )
    
    def log_query(
        self,
        user_id: str,
        query: str,
        query_hash: str,
        result_count: int,
        execution_time_ms: float,
        phi_fields_accessed: Optional[list] = None
    ) -> None:
        """
        Log database query execution.
        
        Args:
            user_id: ID of user executing query
            query: SQL query (sanitized)
            query_hash: Hash of query for tracking
            result_count: Number of results returned
            execution_time_ms: Query execution time
            phi_fields_accessed: List of PHI fields in query results
        """
        self.log_access(
            user_id=user_id,
            action="QUERY_EXECUTE",
            resource="bigquery",
            result="SUCCESS",
            phi_accessed=bool(phi_fields_accessed),
            metadata={
                "query_hash": query_hash,
                "result_count": result_count,
                "execution_time_ms": execution_time_ms,
                "phi_fields": phi_fields_accessed or []
            }
        )
    
    def log_phi_access(
        self,
        user_id: str,
        record_id: str,
        fields_accessed: list,
        purpose: str
    ) -> None:
        """
        Log access to Protected Health Information.
        
        Args:
            user_id: ID of user accessing PHI
            record_id: Identifier of record accessed
            fields_accessed: List of PHI fields accessed
            purpose: Purpose of access (treatment, payment, operations)
        """
        self.log_access(
            user_id=user_id,
            action="PHI_ACCESS",
            resource=f"patient_record:{record_id}",
            result="SUCCESS",
            phi_accessed=True,
            metadata={
                "fields_accessed": fields_accessed,
                "purpose": purpose
            }
        )


class AccessControl:
    """Access control and authorization utilities."""
    
    VALID_ROLES = ["admin", "healthcare_provider", "analyst", "readonly"]
    
    @staticmethod
    def check_phi_access(user_role: str, requested_fields: list) -> bool:
        """
        Check if user role has permission to access PHI fields.
        
        Args:
            user_role: Role of the requesting user
            requested_fields: List of fields being requested
            
        Returns:
            True if access is allowed, False otherwise
        """
        phi_fields = set(settings.phi_fields)
        requested_phi = set(requested_fields) & phi_fields
        
        if not requested_phi:
            return True  # No PHI requested
        
        # Only certain roles can access PHI
        if user_role in ["admin", "healthcare_provider"]:
            return True
        
        logger.warning(
            "phi_access_denied",
            user_role=user_role,
            requested_phi=list(requested_phi)
        )
        return False
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize query for logging (remove potential PHI).
        
        Args:
            query: SQL query string
            
        Returns:
            Sanitized query string
        """
        # Remove potential PHI values from query
        # This is a simple implementation - enhance based on needs
        sanitized = query
        for phi_field in settings.phi_fields:
            # Replace actual values with placeholder
            sanitized = sanitized.replace(phi_field, "[PHI_FIELD]")
        return sanitized


# Global instances
encryption_service = EncryptionService()
audit_logger = AuditLogger()
access_control = AccessControl()