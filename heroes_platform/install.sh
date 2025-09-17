#!/bin/bash

# Heroes Platform Auto-Install Script
# Automatically installs all dependencies and sets up the environment

set -e  # Exit on any error

echo "🎯 Heroes Platform Auto-Install"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "Python 3 found: $(python3 --version)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        print_success "Python found: $(python --version)"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "pip not found. Please install pip"
        exit 1
    fi
    
    print_success "pip found: $($PYTHON_CMD -m pip --version)"
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d ".venv" ]; then
        $PYTHON_CMD -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source .venv/Scripts/activate
    else
        # Unix/Linux/macOS
        source .venv/bin/activate
    fi
    
    print_success "Virtual environment activated"
}

# Install dependencies using setup.py
install_dependencies() {
    print_status "Installing dependencies from pyproject.toml..."
    
    if [ -f "setup.py" ]; then
        $PYTHON_CMD setup.py
    else
        print_error "setup.py not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    dirs=("logs" "output" "data" "config" "tests" "src")
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_warning "Directory already exists: $dir"
        fi
    done
}

# Copy configuration files
copy_configs() {
    print_status "Copying configuration files..."
    
    # Copy pyproject.toml if it exists in parent directory
    if [ -f "../pyproject.toml" ] && [ ! -f "pyproject.toml" ]; then
        cp ../pyproject.toml .
        print_success "Copied pyproject.toml"
    fi
    
    # Copy .env if it exists in parent directory
    if [ -f "../.env" ] && [ ! -f ".env" ]; then
        cp ../.env .
        print_success "Copied .env"
    fi
}

# Run tests to verify installation
run_tests() {
    print_status "Running tests to verify installation..."
    
    if [ -f "run_tests.py" ]; then
        $PYTHON_CMD run_tests.py
        print_success "Tests completed"
    else
        print_warning "run_tests.py not found, skipping tests"
    fi
}

# Main installation function
main() {
    print_status "Starting Heroes Platform installation..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    check_python
    check_pip
    create_venv
    activate_venv
    install_dependencies
    create_directories
    copy_configs
    run_tests
    
    print_success "🎉 Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source .venv/bin/activate"
    echo "2. Start MCP server: cd mcp_server && python run_mcp_server.py"
    echo "3. Run tests: python run_tests.py"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"
