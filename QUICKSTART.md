# Quick Start Guide

Get up and running with the BigQuery LangChain Agent in 5 minutes!

## Prerequisites

- Python 3.9+
- Google Cloud Platform account
- BigQuery dataset
- OpenAI API key

## 1. Installation

### Option A: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd bigquery-langchain-agent

# Run setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create virtual environment
- Install dependencies
- Create necessary directories
- Generate .env file from template

### Option B: Manual Setup

```bash
# Clone and navigate
git clone <your-repo-url>
cd bigquery-langchain-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir logs data credentials

# Copy environment template
cp .env.example .env
```

## 2. Configuration

### A. Environment Variables

Edit `.env` file with your credentials:

```bash
# Google Cloud
GCP_PROJECT_ID=your-gcp-project-id
GCP_DATASET_ID=your-bigquery-dataset
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account-key.json

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Security (generate secure keys)
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

### B. GCP Service Account

1. Create service account in GCP Console
2. Grant permissions:
   - BigQuery Data Viewer
   - BigQuery Job User
3. Download JSON key file
4. Save to `credentials/service-account-key.json`

Quick command:
```bash
# Create service account
gcloud iam service-accounts create bigquery-agent

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

# Download key
gcloud iam service-accounts keys create credentials/service-account-key.json \
  --iam-account=bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 3. Test Your Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
make test

# Or manually
pytest tests/ -v
```

## 4. Run Your First Query

### Option A: Interactive Mode

```bash
python examples/basic_usage.py
```

Example interaction:
```
Your question: What tables are available?
Processing...

Response:
Tables in dataset 'healthcare':
  - patients
  - appointments
  - diagnoses

Your question: Show me the schema for the patients table
Processing...

Response:
Schema for table 'patients':
  id: INTEGER (REQUIRED)
  name: STRING (REQUIRED)
  date_of_birth: DATE
  ...
```

### Option B: Programmatic Usage

```python
from src.agent import BigQueryAgent

# Initialize agent
agent = BigQueryAgent(
    user_id="demo_user",
    user_role="admin"
)

# Ask questions in natural language
result = agent.query("How many patients do we have?")
print(result)

result = agent.query("Show me patients admitted this month")
print(result)
```

## 5. Run as API (Optional)

```bash
# Start API server
python -m uvicorn src.api.main:app --reload

# Or use the shortcut
python src/api/main.py
```

Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Get authentication token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "user_role": "admin"}'

# Query with token
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "What tables are available?"}'
```

## 6. Docker Deployment

```bash
# Build image
docker build -f docker/Dockerfile -t bigquery-agent:latest .

# Run container
docker run -d \
  --name bigquery-agent \
  --env-file .env \
  -v $(pwd)/credentials:/app/credentials:ro \
  -v $(pwd)/logs:/app/logs \
  -p 8000:8000 \
  bigquery-agent:latest

# View logs
docker logs -f bigquery-agent
```

## Common Issues & Solutions

### Issue: "Authentication Error"
**Solution:** Check that:
- Service account key file exists at correct path
- `GOOGLE_APPLICATION_CREDENTIALS` points to the key file
- Service account has necessary permissions

### Issue: "BigQuery dataset not found"
**Solution:** 
- Verify dataset exists: `bq ls YOUR_PROJECT_ID:`
- Check `GCP_DATASET_ID` in .env matches dataset name

### Issue: "Module not found"
**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: "OpenAI API Error"
**Solution:**
- Verify API key is valid
- Check billing is enabled on OpenAI account
- Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

## Next Steps

1. **Security Setup**
   - Review [HIPAA Compliance Guide](docs/HIPAA_COMPLIANCE.md)
   - Sign BAA with Google Cloud
   - Configure encryption keys
   - Set up audit logging

2. **Customize Agent**
   - Modify system prompt in `src/agent/bigquery_agent.py`
   - Add custom tools
   - Configure PHI fields in settings

3. **Production Deployment**
   - Review [Deployment Guide](docs/DEPLOYMENT.md)
   - Set up monitoring
   - Configure CI/CD pipeline
   - Implement rate limiting

4. **Development**
   - Read [Contributing Guide](CONTRIBUTING.md)
   - Run tests: `make test`
   - Check code quality: `make lint`

## Useful Commands

```bash
# Development
make run              # Run the example
make test            # Run tests
make test-cov        # Run tests with coverage
make lint            # Run linting
make format          # Format code

# Docker
make docker-build    # Build Docker image
make docker-run      # Run Docker container

# CI/CD
make ci              # Run full CI pipeline locally
```

## Resources

- [Full README](README.md)
- [HIPAA Compliance](docs/HIPAA_COMPLIANCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing](CONTRIBUTING.md)
- [LangChain Docs](https://python.langchain.com/)
- [BigQuery Docs](https://cloud.google.com/bigquery/docs)

## Support

- 📖 Documentation: Check `docs/` directory
- 🐛 Issues: Open a GitHub issue
- 💬 Discussions: Use GitHub Discussions
- 📧 Email: support@yourorganization.com

---

**Ready to build HIPAA-compliant AI agents! 🏥🤖🔒**
