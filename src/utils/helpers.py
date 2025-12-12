"""
Utility functions for the BigQuery LangChain Agent.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


def generate_query_hash(query: str) -> str:
    """
    Generate a unique hash for a query.
    
    Args:
        query: SQL query string
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(query.encode()).hexdigest()


def sanitize_for_logging(data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitize data for logging by removing/masking sensitive information.
    
    Args:
        data: Dictionary to sanitize
        sensitive_keys: List of keys to mask (default: common PHI fields)
        
    Returns:
        Sanitized dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = ["ssn", "password", "api_key", "token", "secret"]
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_logging(value, sensitive_keys)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_for_logging(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as ISO 8601 string in UTC.
    
    Args:
        dt: Datetime to format (default: current UTC time)
        
    Returns:
        ISO 8601 formatted string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    return dt.isoformat()


def parse_bigquery_results(results: Any, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Parse BigQuery results into list of dictionaries.
    
    Args:
        results: BigQuery query results
        limit: Maximum number of results to return
        
    Returns:
        List of result rows as dictionaries
    """
    rows = []
    for i, row in enumerate(results):
        if limit and i >= limit:
            break
        rows.append(dict(row))
    
    return rows


def validate_gcp_project_id(project_id: str) -> bool:
    """
    Validate GCP project ID format.
    
    Args:
        project_id: GCP project ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    # GCP project IDs must:
    # - Be 6-30 characters
    # - Start with lowercase letter
    # - Contain only lowercase letters, digits, and hyphens
    if not project_id:
        return False
    
    if len(project_id) < 6 or len(project_id) > 30:
        return False
    
    if not project_id[0].islower():
        return False
    
    for char in project_id:
        if not (char.islower() or char.isdigit() or char == '-'):
            return False
    
    return True


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"


def is_valid_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Function result if successful
        
    Raises:
        Last exception if all retries fail
    """
    import time
    
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(
                    "retry_attempt",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    delay=delay,
                    error=str(e)
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(
                    "retry_failed",
                    attempts=max_retries + 1,
                    error=str(e)
                )
    
    raise last_exception


def get_environment_info() -> Dict[str, Any]:
    """
    Get information about the current environment.
    
    Returns:
        Dictionary with environment information
    """
    import platform
    import sys
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }
