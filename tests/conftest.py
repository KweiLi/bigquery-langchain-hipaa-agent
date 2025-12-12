"""
Pytest configuration and fixtures for testing.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from google.cloud import bigquery


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    os.environ.update({
        "GCP_PROJECT_ID": "test-project",
        "GCP_DATASET_ID": "test-dataset",
        "GCP_LOCATION": "US",
        "GOOGLE_APPLICATION_CREDENTIALS": "test-credentials.json",
        "OPENAI_API_KEY": "test-key",
        "LLM_MODEL": "gpt-4",
        "LLM_TEMPERATURE": "0.0",
        "MAX_TOKENS": "2000",
        "ENCRYPTION_KEY": "test-encryption-key-32-bytes!!",
        "JWT_SECRET_KEY": "test-jwt-secret",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "ENABLE_AUDIT_LOG": "true",
        "ENVIRONMENT": "test",
        "APP_NAME": "BigQuery-LangChain-Agent",
        "APP_VERSION": "1.0.0",
        "API_PORT": "8000",
        "ENABLE_ENCRYPTION": "true",
        "ENABLE_AUDIT_TRAIL": "true",
        "DATA_RETENTION_DAYS": "2555",
        "MAX_QUERIES_PER_MINUTE": "10",
        "MAX_QUERIES_PER_HOUR": "100",
        "BIGQUERY_MAX_RESULTS": "1000",
        "BIGQUERY_TIMEOUT_SECONDS": "300",
        "ENABLE_QUERY_CACHE": "true",
    })
    yield
    # Cleanup if needed


@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client."""
    with patch('google.cloud.bigquery.Client') as mock_client:
        # Configure mock
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        
        # Mock query results
        mock_job = MagicMock()
        mock_job.result.return_value = []
        mock_instance.query.return_value = mock_job
        
        yield mock_instance


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch('langchain_openai.ChatOpenAI') as mock_openai:
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_credentials():
    """Mock Google Cloud credentials."""
    with patch('google.oauth2.service_account.Credentials') as mock_creds:
        mock_instance = MagicMock()
        mock_creds.from_service_account_file.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_query_results():
    """Sample BigQuery query results."""
    return [
        {"id": 1, "name": "Test Patient 1", "age": 45},
        {"id": 2, "name": "Test Patient 2", "age": 52},
    ]


@pytest.fixture
def sample_table_schema():
    """Sample BigQuery table schema."""
    return [
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("age", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("diagnosis", "STRING", mode="NULLABLE"),
    ]
