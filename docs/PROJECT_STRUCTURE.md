# Project Structure

This document explains the organization of the BigQuery LangChain Agent project.

## Directory Tree

```
bigquery-langchain-agent/
│
├── .github/                      # GitHub configuration
│   └── workflows/
│       └── ci-cd.yml            # CI/CD pipeline
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── agent/                   # LangChain agent implementation
│   │   ├── __init__.py
│   │   └── bigquery_agent.py   # Main agent class
│   │
│   ├── api/                     # REST API (optional)
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI application
│   │
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py         # Settings with Pydantic
│   │
│   ├── security/                # Security and HIPAA compliance
│   │   ├── __init__.py
│   │   └── hipaa_compliance.py # Encryption, audit, access control
│   │
│   └── utils/                   # Utility functions
│       └── __init__.py
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_agent.py           # Agent tests
│   ├── test_config.py          # Configuration tests
│   └── test_security.py        # Security tests
│
├── examples/                    # Example usage
│   └── basic_usage.py          # Interactive demo
│
├── docs/                        # Documentation
│   ├── HIPAA_COMPLIANCE.md     # HIPAA compliance guide
│   └── DEPLOYMENT.md           # Deployment instructions
│
├── docker/                      # Docker configuration
│   ├── Dockerfile              # Container definition
│   └── docker-compose.yml      # Multi-container setup
│
├── logs/                        # Application logs (gitignored)
├── data/                        # Data directory (gitignored)
├── credentials/                 # GCP credentials (gitignored)
│
├── .env.example                 # Environment template
├── .env                         # Environment variables (gitignored)
├── .gitignore                   # Git ignore patterns
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── Makefile                     # Development shortcuts
├── setup.sh                     # Setup automation script
├── README.md                    # Project overview
├── QUICKSTART.md               # Quick start guide
├── CONTRIBUTING.md             # Contribution guidelines
└── LICENSE                     # MIT License

```

## Component Details

### Source Code (`src/`)

#### Agent Module (`src/agent/`)
The core AI agent implementation using LangChain.

**Key Files:**
- `bigquery_agent.py`: Main `BigQueryAgent` class
  - Initializes LangChain agent
  - Creates BigQuery and schema tools
  - Handles query execution
  - Implements security checks
  - Manages audit logging

**Key Classes:**
- `BigQueryAgent`: Main agent class

**Key Methods:**
- `__init__()`: Initialize agent with user credentials
- `query()`: Execute natural language queries
- `_create_bigquery_tool()`: Create tool for querying BigQuery
- `_create_schema_tool()`: Create tool for schema exploration
- `_validate_query()`: Security validation of SQL queries
- `_detect_phi_fields()`: Detect PHI in results

#### API Module (`src/api/`)
Optional REST API implementation using FastAPI.

**Key Files:**
- `main.py`: FastAPI application
  - Authentication endpoints
  - Query execution endpoints
  - Health check endpoint
  - Schema retrieval endpoint

**Endpoints:**
- `GET /`: Root endpoint
- `GET /health`: Health check
- `POST /auth/token`: Get JWT token
- `POST /query`: Execute query (requires auth)
- `GET /schema`: Get database schema (requires auth)

#### Config Module (`src/config/`)
Configuration management using Pydantic settings.

**Key Files:**
- `settings.py`: Settings class with validation
  - Environment variable loading
  - Default values
  - Validation rules
  - HIPAA compliance checks

**Key Classes:**
- `Settings`: Configuration with Pydantic validation

**Configuration Sections:**
- GCP Configuration
- LLM Configuration
- Security Settings
- HIPAA Compliance Settings
- Rate Limiting
- BigQuery Settings

#### Security Module (`src/security/`)
HIPAA compliance and security utilities.

**Key Files:**
- `hipaa_compliance.py`: Security implementations
  - Encryption/decryption
  - Audit logging
  - Access control

**Key Classes:**
- `EncryptionService`: Encrypt/decrypt PHI
- `AuditLogger`: Comprehensive audit logging
- `AccessControl`: Role-based access control

**Security Features:**
- AES encryption for PHI
- SHA-256 hashing for indexing
- Structured audit logs (JSON)
- Role-based permissions
- Query sanitization

### Tests (`tests/`)

**Test Organization:**
- `conftest.py`: Shared fixtures and test configuration
- `test_agent.py`: Agent functionality tests
- `test_config.py`: Configuration validation tests
- `test_security.py`: Security and HIPAA tests

**Test Markers:**
- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.security`: Security-focused tests
- `@pytest.mark.slow`: Slow-running tests

### Documentation (`docs/`)

- **HIPAA_COMPLIANCE.md**: Comprehensive HIPAA guide
  - Administrative safeguards
  - Physical safeguards
  - Technical safeguards
  - BAA requirements
  - Breach notification procedures

- **DEPLOYMENT.md**: Deployment instructions
  - Local development setup
  - Docker deployment
  - GCP deployment options
  - Production checklist
  - Monitoring and maintenance

### Docker (`docker/`)

- **Dockerfile**: Multi-stage build
  - Builder stage for dependencies
  - Production stage with minimal image
  - Non-root user for security
  - Health checks

- **docker-compose.yml**: Service orchestration
  - Application service
  - Volume mounts
  - Network configuration
  - Resource limits
  - Optional monitoring services

### Configuration Files

#### `.env.example`
Template for environment variables with placeholders.

#### `requirements.txt`
Python dependencies with specific versions:
- Core: langchain, google-cloud-bigquery
- Security: cryptography, pyjwt
- API: fastapi, uvicorn
- Testing: pytest, pytest-cov
- Development: black, flake8, mypy

#### `pytest.ini`
Pytest configuration:
- Test discovery patterns
- Coverage settings
- Test markers
- Command-line options

#### `Makefile`
Development commands:
- `make install`: Install dependencies
- `make test`: Run tests
- `make lint`: Run linting
- `make format`: Format code
- `make docker-build`: Build Docker image
- `make run`: Run application

## File Dependencies

### Import Flow

```
examples/basic_usage.py
    ↓
src/__init__.py
    ↓
src/agent/__init__.py
    ↓
src/agent/bigquery_agent.py
    ├─→ src/config/settings.py
    └─→ src/security/hipaa_compliance.py
```

### Configuration Loading

```
.env file
    ↓
src/config/settings.py (Pydantic)
    ↓
Settings object (globally available)
    ↓
Used by all modules
```

### Security Flow

```
User Request
    ↓
Authentication (JWT)
    ↓
Authorization (RBAC)
    ↓
Query Validation
    ↓
Audit Logging
    ↓
Query Execution
    ↓
PHI Detection
    ↓
Audit Logging
    ↓
Encrypted Response
```

## Key Design Patterns

### 1. Dependency Injection
Settings and services are injected rather than hardcoded:
```python
def __init__(self, user_id: str, credentials_path: Optional[str] = None):
    self.config = get_settings()
    ...
```

### 2. Factory Pattern
Tools are created through factory methods:
```python
def _create_bigquery_tool(self) -> Tool:
    # Create and configure tool
    return Tool(...)
```

### 3. Strategy Pattern
Different access control strategies based on role:
```python
@staticmethod
def check_phi_access(user_role: str, requested_fields: list) -> bool:
    if user_role in ["admin", "healthcare_provider"]:
        return True
    # Other strategies...
```

### 4. Singleton Pattern
Global instances for services:
```python
encryption_service = EncryptionService()
audit_logger = AuditLogger()
```

## Code Organization Principles

### 1. Separation of Concerns
- Agent logic separated from security
- Configuration separated from implementation
- API separated from core logic

### 2. Single Responsibility
- Each class has one main purpose
- Small, focused functions
- Clear module boundaries

### 3. DRY (Don't Repeat Yourself)
- Reusable utilities
- Shared fixtures in tests
- Common configurations

### 4. Security First
- Security checks at multiple levels
- Audit logging throughout
- Encryption by default

## Adding New Features

### Adding a New Tool

1. Create tool in `src/agent/bigquery_agent.py`:
```python
def _create_your_tool(self) -> Tool:
    def tool_function(input: str) -> str:
        # Implementation
        pass
    
    return Tool(
        name="your_tool",
        description="Tool description",
        func=tool_function
    )
```

2. Add to tools list in `_create_agent()`:
```python
tools = [
    self._create_bigquery_tool(),
    self._create_schema_tool(),
    self._create_your_tool(),  # Add here
]
```

### Adding New Configuration

1. Add to `src/config/settings.py`:
```python
class Settings(BaseSettings):
    your_setting: str = Field(..., description="Your setting")
```

2. Add to `.env.example`:
```
YOUR_SETTING=default-value
```

### Adding New Tests

1. Create test file in `tests/`:
```python
# tests/test_your_feature.py
import pytest

def test_your_feature():
    # Test implementation
    pass
```

2. Add marker if needed:
```python
@pytest.mark.integration
def test_integration_feature():
    pass
```

## Best Practices

### 1. Always Use Type Hints
```python
def process_query(query: str, user_id: str) -> QueryResult:
    ...
```

### 2. Document with Docstrings
```python
def function(param: str) -> str:
    """
    Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
    """
```

### 3. Handle Errors Gracefully
```python
try:
    result = execute_query(query)
except Exception as e:
    logger.error("query_failed", error=str(e))
    audit_logger.log_access(..., result="ERROR")
    raise
```

### 4. Log Important Events
```python
logger.info("query_executed", user_id=user_id, query_hash=hash)
audit_logger.log_query(...)
```

## Maintenance

### Regular Tasks

1. **Dependencies**: Update monthly
   ```bash
   make upgrade-deps
   ```

2. **Security Scan**: Run weekly
   ```bash
   make security-scan
   ```

3. **Tests**: Run before commits
   ```bash
   make pre-commit
   ```

4. **Documentation**: Update with changes

### Version Control

- Use feature branches
- Write clear commit messages
- Tag releases
- Maintain CHANGELOG

---

For more details, see:
- [README.md](../README.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [QUICKSTART.md](../QUICKSTART.md)
