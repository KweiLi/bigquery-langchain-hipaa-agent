# Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Google Cloud Platform Deployment](#google-cloud-platform-deployment)
5. [Production Checklist](#production-checklist)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required

- Python 3.9 or higher
- Google Cloud Platform account
- BigQuery dataset created
- OpenAI API key (or alternative LLM provider)
- Docker (for containerized deployment)

### GCP Services Required

- BigQuery API enabled
- Cloud Storage (for audit logs)
- Secret Manager (recommended for production)
- Cloud Logging (for centralized logging)

## Local Development

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd bigquery-langchain-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:
```bash
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=your-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
OPENAI_API_KEY=sk-your-key
ENCRYPTION_KEY=generate-secure-key-here
```

### 3. Service Account Setup

```bash
# Create service account
gcloud iam service-accounts create bigquery-agent \
    --display-name="BigQuery Agent Service Account"

# Grant BigQuery permissions
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

### 4. Run Locally

```bash
# Run the example script
python examples/basic_usage.py

# Or use the Makefile
make run
```

### 5. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
```

## Docker Deployment

### 1. Build Docker Image

```bash
# Build the image
docker build -f docker/Dockerfile -t bigquery-agent:latest .

# Or use docker-compose
cd docker
docker-compose build
```

### 2. Run with Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### 3. Environment Variables for Docker

Create a `.env` file in the docker directory:

```bash
# Copy from root .env
cp ../.env .env

# Or create docker-specific .env
cat > .env << EOF
GCP_PROJECT_ID=your-project-id
GCP_DATASET_ID=your-dataset-id
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service-account-key.json
OPENAI_API_KEY=sk-your-key
ENVIRONMENT=production
EOF
```

Mount credentials:
```bash
docker run -d \
  --name bigquery-agent \
  --env-file .env \
  -v /path/to/credentials:/app/credentials:ro \
  -v /path/to/logs:/app/logs \
  bigquery-agent:latest
```

## Google Cloud Platform Deployment

### Option 1: Cloud Run (Recommended for production)

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bigquery-agent

# Deploy to Cloud Run
gcloud run deploy bigquery-agent \
  --image gcr.io/YOUR_PROJECT_ID/bigquery-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID \
  --set-env-vars GCP_DATASET_ID=YOUR_DATASET_ID \
  --service-account bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

### Option 2: Google Kubernetes Engine (GKE)

```bash
# Create GKE cluster
gcloud container clusters create bigquery-agent-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=us-central1

# Get credentials
gcloud container clusters get-credentials bigquery-agent-cluster \
  --region=us-central1

# Create Kubernetes secret for credentials
kubectl create secret generic gcp-credentials \
  --from-file=key.json=credentials/service-account-key.json

# Apply Kubernetes manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### Option 3: Compute Engine

```bash
# Create VM instance
gcloud compute instances create bigquery-agent-vm \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=n1-standard-2 \
  --zone=us-central1-a \
  --service-account=bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --scopes=cloud-platform

# SSH into instance
gcloud compute ssh bigquery-agent-vm --zone=us-central1-a

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Pull and run container
sudo docker pull gcr.io/YOUR_PROJECT_ID/bigquery-agent:latest
sudo docker run -d \
  --name bigquery-agent \
  --restart unless-stopped \
  -p 8000:8000 \
  gcr.io/YOUR_PROJECT_ID/bigquery-agent:latest
```

## Production Checklist

### Security

- [ ] Service account uses least privilege principle
- [ ] Encryption keys stored in Secret Manager
- [ ] TLS/SSL certificates configured
- [ ] VPC and firewall rules configured
- [ ] Cloud Armor enabled (DDoS protection)
- [ ] IAM policies reviewed and documented
- [ ] Audit logging enabled in GCP
- [ ] BAA signed with Google Cloud

### Configuration

- [ ] Environment set to "production"
- [ ] Debug mode disabled
- [ ] Appropriate resource limits set
- [ ] Rate limiting configured
- [ ] Timeout values tuned
- [ ] Log level set to INFO or WARNING
- [ ] Error tracking integrated (Sentry, etc.)

### Monitoring

- [ ] Cloud Monitoring dashboards created
- [ ] Alerts configured for:
  - High error rates
  - Slow queries
  - Resource exhaustion
  - Security events
- [ ] Uptime checks configured
- [ ] Log-based metrics created

### Backup and Recovery

- [ ] BigQuery dataset backup schedule
- [ ] Audit log retention policy
- [ ] Disaster recovery plan documented
- [ ] Backup restoration tested

### Compliance

- [ ] HIPAA compliance verified
- [ ] All BAAs in place
- [ ] Privacy impact assessment completed
- [ ] Security audit performed
- [ ] Incident response plan documented
- [ ] Staff training completed

## Monitoring and Maintenance

### Cloud Monitoring Dashboard

```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

### Key Metrics to Monitor

1. **Performance**
   - Query execution time
   - API response time
   - Resource utilization (CPU, Memory)

2. **Security**
   - Failed authentication attempts
   - PHI access patterns
   - Unusual query patterns

3. **Reliability**
   - Error rates
   - Success rates
   - Uptime percentage

### Log Analysis

```bash
# View application logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=bigquery-agent" \
  --limit 50 \
  --format json

# Query audit logs
gcloud logging read "jsonPayload.event_type=audit" \
  --limit 100 \
  --format json

# Export logs to BigQuery for analysis
gcloud logging sinks create bigquery-export \
  bigquery.googleapis.com/projects/YOUR_PROJECT_ID/datasets/logs \
  --log-filter='resource.type="cloud_run_revision"'
```

### Health Checks

```bash
# Cloud Run health check
curl https://your-service-url.run.app/health

# Docker health check
docker inspect --format='{{.State.Health.Status}}' bigquery-agent
```

### Updates and Maintenance

```bash
# Pull latest changes
git pull origin main

# Run tests
pytest

# Build new image
docker build -t bigquery-agent:latest .

# Deploy new version
gcloud run deploy bigquery-agent \
  --image gcr.io/YOUR_PROJECT_ID/bigquery-agent:latest \
  --platform managed
```

### Scaling

```bash
# Cloud Run auto-scales, but you can set limits
gcloud run services update bigquery-agent \
  --min-instances=1 \
  --max-instances=10 \
  --concurrency=80

# GKE horizontal pod autoscaling
kubectl autoscale deployment bigquery-agent \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify service account permissions
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.members:serviceAccount:bigquery-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com"
   ```

2. **BigQuery Access Errors**
   ```bash
   # Test BigQuery access
   bq query --use_legacy_sql=false \
     'SELECT 1 as test'
   ```

3. **Memory Issues**
   ```bash
   # Increase memory limit
   docker update bigquery-agent --memory=4g
   
   # Or in Cloud Run
   gcloud run services update bigquery-agent --memory=4Gi
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python examples/basic_usage.py
```

### Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review documentation in `docs/`
- Open GitHub issue
- Contact: support@yourorganization.com

## Additional Resources

- [GCP Documentation](https://cloud.google.com/docs)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [LangChain Documentation](https://python.langchain.com/)
- [HIPAA Compliance Guide](docs/HIPAA_COMPLIANCE.md)
