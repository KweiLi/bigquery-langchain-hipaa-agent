# Contributing to BigQuery LangChain Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Maintain professional communication
- Protect sensitive information (no PHI in issues/PRs)

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Google Cloud Platform account (for testing)
- Understanding of HIPAA compliance requirements

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/bigquery-langchain-agent.git
   cd bigquery-langchain-agent
   ```

2. **Set up development environment**
   ```bash
   make init-project
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your test credentials
   ```

4. **Run tests**
   ```bash
   make test
   ```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Emergency fixes for production

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

3. **Write tests**
   ```bash
   # Add tests in tests/ directory
   pytest tests/test_your_feature.py
   ```

4. **Format and lint**
   ```bash
   make format
   make lint
   ```

5. **Run all tests**
   ```bash
   make test-cov
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `security`: Security-related changes (important for HIPAA)

Examples:
```
feat: add query caching mechanism
fix: resolve authentication token expiration issue
docs: update HIPAA compliance documentation
security: implement additional encryption for PHI fields
```

## Code Standards

### Python Style Guide

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

Example:
```python
def process_query(query: str, user_id: str) -> QueryResult:
    """
    Process a user query and return results.
    
    Args:
        query: Natural language query string
        user_id: Identifier of the user making the query
        
    Returns:
        QueryResult object containing processed results
        
    Raises:
        ValidationError: If query is invalid
        AuthorizationError: If user lacks permissions
    """
    # Implementation
    pass
```

### Code Quality

- **Linting**: Code must pass flake8, pylint checks
- **Type checking**: Code must pass mypy checks
- **Security**: Code must pass bandit security checks
- **Testing**: Minimum 80% code coverage
- **Documentation**: All public APIs must be documented

### Testing Guidelines

1. **Unit Tests**
   - Test individual components in isolation
   - Mock external dependencies
   - Fast execution (<1s per test)

2. **Integration Tests**
   - Test component interactions
   - Use test datasets
   - Mark with `@pytest.mark.integration`

3. **Security Tests**
   - Test access controls
   - Test encryption/decryption
   - Test audit logging
   - Mark with `@pytest.mark.security`

Example:
```python
import pytest
from src.security import AccessControl

@pytest.mark.security
def test_phi_access_control():
    """Test that PHI access is properly controlled."""
    result = AccessControl.check_phi_access(
        user_role="analyst",
        requested_fields=["name", "ssn"]
    )
    assert result is False
```

## Security Considerations

### HIPAA Compliance

- Never commit PHI (Protected Health Information)
- Never commit real credentials
- Always encrypt sensitive data
- Implement proper access controls
- Maintain audit logs

### Sensitive Information

**Never commit:**
- API keys
- Service account credentials
- Encryption keys
- Patient data
- Real database connection strings

**Use instead:**
- Environment variables
- Secret managers
- Mock data for testing
- Placeholder values in examples

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code is formatted and linted
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if applicable)
- [ ] No security issues found
- [ ] No PHI or credentials in code

### Submitting PR

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use descriptive title
   - Reference related issues
   - Describe changes clearly
   - Add screenshots if relevant

3. **PR Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   - [ ] Security enhancement
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] All tests pass
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No PHI or credentials included
   - [ ] HIPAA compliance maintained
   
   ## Related Issues
   Fixes #123
   ```

4. **Code Review**
   - Address reviewer feedback
   - Make requested changes
   - Re-request review when ready

### Review Criteria

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Security considerations
- HIPAA compliance
- Performance implications

## Documentation

### What to Document

- New features
- API changes
- Configuration options
- Deployment procedures
- Security considerations

### Where to Document

- **Code**: Docstrings and comments
- **README.md**: Project overview
- **docs/**: Detailed documentation
  - HIPAA_COMPLIANCE.md
  - DEPLOYMENT.md
  - API.md (if applicable)

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Test thoroughly
5. Create GitHub release
6. Deploy to production

## Getting Help

### Resources

- **Documentation**: Check `docs/` directory
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions

### Contact

- **General Questions**: Open a GitHub issue
- **Security Issues**: Email security@yourorganization.com
- **Urgent Issues**: Contact maintainers directly

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Mentioned in documentation (optional)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to make healthcare AI more secure and compliant! 🏥🤖🔒
