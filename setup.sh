#!/bin/bash

# BigQuery LangChain Agent Setup Script
# This script helps set up the development environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# Main script
print_header "BigQuery LangChain Agent Setup"

# Check prerequisites
print_info "Checking prerequisites..."

PREREQS_OK=true

if ! check_command python3; then
    print_error "Please install Python 3.9 or higher"
    PREREQS_OK=false
fi

if ! check_command pip3; then
    print_error "Please install pip3"
    PREREQS_OK=false
fi

if ! check_command git; then
    print_error "Please install git"
    PREREQS_OK=false
fi

if [ "$PREREQS_OK" = false ]; then
    print_error "Please install missing prerequisites and try again"
    exit 1
fi

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9 or higher required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python version: $PYTHON_VERSION"

# Create virtual environment
print_header "Creating Virtual Environment"
if [ -d "venv" ]; then
    print_info "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
print_header "Installing Dependencies"
print_info "This may take a few minutes..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependencies installed"

# Install development dependencies
print_info "Installing development dependencies..."
pip install black flake8 mypy pylint isort bandit pytest-watch > /dev/null 2>&1
print_success "Development dependencies installed"

# Create directories
print_header "Creating Project Directories"
mkdir -p logs
mkdir -p data
mkdir -p credentials
print_success "Directories created"

# Create .env file
print_header "Configuring Environment"
if [ -f ".env" ]; then
    print_info ".env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        print_success ".env file created from template"
    fi
else
    cp .env.example .env
    print_success ".env file created from template"
fi

# Run tests
print_header "Running Tests"
read -p "Do you want to run tests now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    print_info "Running tests..."
    if pytest tests/ -v; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed. This is expected if GCP credentials are not configured."
    fi
fi

# Summary
print_header "Setup Complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your .env file:"
echo "   ${YELLOW}nano .env${NC}  # or use your preferred editor"
echo ""
echo "2. Add your GCP service account credentials:"
echo "   ${YELLOW}cp /path/to/your/service-account-key.json credentials/${NC}"
echo ""
echo "3. Update the GOOGLE_APPLICATION_CREDENTIALS path in .env:"
echo "   ${YELLOW}GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account-key.json${NC}"
echo ""
echo "4. Set up your OpenAI API key in .env:"
echo "   ${YELLOW}OPENAI_API_KEY=sk-your-api-key${NC}"
echo ""
echo "5. Activate the virtual environment:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "6. Run the example:"
echo "   ${YELLOW}python examples/basic_usage.py${NC}"
echo ""
echo "7. Or use the Makefile:"
echo "   ${YELLOW}make run${NC}"
echo ""
echo "For more information, see:"
echo "  - README.md"
echo "  - docs/DEPLOYMENT.md"
echo "  - docs/HIPAA_COMPLIANCE.md"
echo ""
print_success "Happy coding! 🚀"
echo ""
