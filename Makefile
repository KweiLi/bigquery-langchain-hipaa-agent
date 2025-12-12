.PHONY: help install test lint format clean run docker-build docker-run setup

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
ISORT := $(PYTHON) -m isort
BANDIT := $(PYTHON) -m bandit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	@echo "Setting up development environment..."
	$(PYTHON) -m venv venv
	@echo "Activating virtual environment and installing dependencies..."
	@echo "Please run: source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)"
	@echo "Then run: make install"

install: ## Install dependencies
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed"

install-dev: install ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install black flake8 mypy pylint isort bandit pytest-watch
	@echo "✓ Development dependencies installed"

test: ## Run tests
	@echo "Running tests..."
	$(PYTEST) tests/ -v
	@echo "✓ Tests completed"

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term-missing -v
	@echo "✓ Coverage report generated in htmlcov/"

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	$(PYTHON) -m pytest_watch tests/ -- -v

test-security: ## Run security tests only
	@echo "Running security tests..."
	$(PYTEST) tests/ -m security -v

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	$(PYTEST) tests/ -m unit -v

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	$(PYTEST) tests/ -m integration -v

lint: ## Run linting checks
	@echo "Running linting checks..."
	$(FLAKE8) src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	$(MYPY) src/ --ignore-missing-imports --no-strict-optional
	@echo "✓ Linting checks passed"

lint-security: ## Run security linting
	@echo "Running security linting..."
	$(BANDIT) -r src/ -f screen
	@echo "✓ Security linting completed"

format: ## Format code with black and isort
	@echo "Formatting code..."
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/
	@echo "✓ Code formatted"

format-check: ## Check code formatting
	@echo "Checking code formatting..."
	$(BLACK) --check src/ tests/
	$(ISORT) --check-only src/ tests/
	@echo "✓ Format check completed"

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	@echo "✓ Cleanup completed"

run: ## Run the example application
	@echo "Running application..."
	$(PYTHON) examples/basic_usage.py

docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -f docker/Dockerfile -t bigquery-agent:latest .
	@echo "✓ Docker image built"

docker-run: ## Run Docker container
	@echo "Running Docker container..."
	docker run -it --rm \
		--env-file .env \
		-v $(PWD)/credentials:/app/credentials:ro \
		-v $(PWD)/logs:/app/logs \
		bigquery-agent:latest

docker-compose-up: ## Start services with docker-compose
	@echo "Starting services..."
	cd docker && docker-compose up -d
	@echo "✓ Services started"

docker-compose-down: ## Stop services with docker-compose
	@echo "Stopping services..."
	cd docker && docker-compose down
	@echo "✓ Services stopped"

docker-compose-logs: ## View docker-compose logs
	cd docker && docker-compose logs -f

security-scan: ## Run security vulnerability scan
	@echo "Running security scan..."
	$(BANDIT) -r src/ -f json -o bandit-report.json
	@echo "✓ Security scan completed (see bandit-report.json)"

check-env: ## Check if .env file exists and is configured
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Copy .env.example to .env and configure it."; \
		exit 1; \
	else \
		echo "✓ .env file exists"; \
	fi

pre-commit: format lint test ## Run pre-commit checks (format, lint, test)
	@echo "✓ Pre-commit checks passed"

ci: format-check lint test-cov ## Run CI pipeline locally
	@echo "✓ CI pipeline completed"

docs: ## Generate documentation
	@echo "Documentation is in docs/ directory"
	@echo "- README.md: Project overview"
	@echo "- HIPAA_COMPLIANCE.md: HIPAA compliance guide"
	@echo "- DEPLOYMENT.md: Deployment guide"

requirements: ## Update requirements.txt
	@echo "Updating requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "✓ Requirements updated"

upgrade-deps: ## Upgrade dependencies
	@echo "Upgrading dependencies..."
	$(PIP) install --upgrade -r requirements.txt
	@echo "✓ Dependencies upgraded"

init-project: setup install-dev ## Initialize new project (setup + install dev deps)
	@echo "Creating .env file from template..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "Creating directories..."
	@mkdir -p logs data credentials
	@echo "✓ Project initialized"
	@echo ""
	@echo "Next steps:"
	@echo "1. Activate virtual environment: source venv/bin/activate"
	@echo "2. Configure .env file with your credentials"
	@echo "3. Run tests: make test"
	@echo "4. Run application: make run"
