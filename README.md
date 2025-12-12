# BigQuery LangChain AI Agent - HIPAA Compliant

A simple, HIPAA-compliant AI agent built with LangChain and BigQuery for learning purposes.

## Overview

This project demonstrates how to build a basic AI agent that can query BigQuery databases while maintaining HIPAA compliance standards.

## Features

- 🤖 LangChain-powered AI agent
- 📊 BigQuery integration
- 🔒 HIPAA compliance measures
- 🚀 CI/CD pipeline with GitHub Actions
- 🐳 Docker containerization
- 📝 Comprehensive logging and audit trails
- 🔐 Encryption at rest and in transit

## Project Structure

```
bigquery-langchain-agent/
├── src/
│   ├── agent/          # LangChain agent implementation
│   ├── config/         # Configuration management
│   ├── security/       # Security and HIPAA compliance utilities
│   └── utils/          # Helper functions
├── tests/              # Unit and integration tests
├── .github/
│   └── workflows/      # CI/CD pipelines
├── docker/             # Docker configuration
├── docs/               # Documentation
├── requirements.txt    # Python dependencies
└── README.md
```

## HIPAA Compliance Features

1. **Data Encryption**: All data encrypted in transit (TLS) and at rest
2. **Access Controls**: Role-based access control (RBAC)
3. **Audit Logging**: Comprehensive activity logging
4. **Data Minimization**: Only queries necessary data
5. **Secure Configuration**: Environment-based secrets management
6. **Session Management**: Secure session handling
7. **BAA Requirement**: Ensure BigQuery has a Business Associate Agreement

## Prerequisites

- Python 3.9+
- Google Cloud Platform account with BigQuery enabled
- Google Cloud Service Account with appropriate permissions
- OpenAI API key (or other LLM provider)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd bigquery-langchain-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Create a `.env` file with the following variables:

```
# Google Cloud
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=your-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# LangChain/LLM
OPENAI_API_KEY=your-openai-key
LLM_MODEL=gpt-4

# Security
ENCRYPTION_KEY=your-encryption-key
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

## Usage

```python
from src.agent.bigquery_agent import BigQueryAgent

# Initialize the agent
agent = BigQueryAgent()

# Query the database
result = agent.query("Show me patient demographics for the last month")

print(result)
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Docker Deployment

```bash
# Build the image
docker build -f docker/Dockerfile -t bigquery-agent:latest .

# Run the container
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  bigquery-agent:latest
```

## CI/CD Pipeline

The project uses GitHub Actions for:
- Automated testing on push/PR
- Code quality checks (linting, type checking)
- Security scanning
- Docker image building
- Deployment to staging/production

## Security Best Practices

1. **Never commit secrets**: Use environment variables or secret managers
2. **Service Account Permissions**: Use least privilege principle
3. **Network Security**: Use VPC and firewall rules
4. **Data Access Logging**: Enable BigQuery audit logs
5. **Regular Updates**: Keep dependencies updated
6. **PHI Handling**: Follow HIPAA guidelines for Protected Health Information

## HIPAA Compliance Checklist

- [ ] Business Associate Agreement (BAA) with Google Cloud
- [ ] Encryption enabled for data at rest and in transit
- [ ] Access controls and authentication implemented
- [ ] Audit logging enabled and monitored
- [ ] Data backup and disaster recovery plan
- [ ] Incident response plan documented
- [ ] Regular security assessments scheduled
- [ ] Staff training on HIPAA requirements

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues or questions, please open a GitHub issue.
