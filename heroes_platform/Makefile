# Heroes Platform Makefile
# Provides convenient commands for project management

.PHONY: help install install-dev install-prod test clean setup venv deps run-server run-tests lint format check-all docs docs-serve docs-build

# Default target
help:
	@echo "🎯 Heroes Platform - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install      - Install all dependencies (dev + production)"
	@echo "  install-dev  - Install development dependencies only"
	@echo "  install-prod - Install production dependencies only"
	@echo "  setup        - Complete setup (venv + deps + config)"
	@echo "  venv         - Create virtual environment"
	@echo "  deps         - Install dependencies from pyproject.toml"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test         - Run all tests"
	@echo "  test-mcp-logs - Run MCP logs monitoring tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage - Run tests with coverage report"
	@echo ""
	@echo "🔧 Development:"
	@echo "  lint         - Run linting (ruff, mypy)"
	@echo "  format       - Format code (black, isort)"
	@echo "  check-all    - Run all checks (lint + format + test)"
	@echo ""
	@echo "🚀 Running:"
	@echo "  run-server   - Start MCP server"
	@echo "  run-tests    - Run test suite"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs         - Build documentation"
	@echo "  docs-serve   - Serve documentation locally"
	@echo "  docs-build   - Build and validate documentation"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean        - Clean build artifacts and cache"
	@echo "  clean-venv   - Remove virtual environment"
	@echo ""

# Installation targets
install: deps
	@echo "✅ All dependencies installed"

install-dev: venv
	@echo "📦 Installing development dependencies..."
	python -m pip install -e ".[dev]"
	@echo "✅ Development dependencies installed"

install-prod: venv
	@echo "📦 Installing production dependencies..."
	python -m pip install -e ".[production]"
	@echo "✅ Production dependencies installed"

setup: venv deps setup-mcp
	@echo "🔧 Setting up project structure..."
	@mkdir -p logs output data config tests src
	@echo "📄 Copying configuration files..."
	@if [ ! -f "pyproject.toml" ]; then echo "❌ pyproject.toml not found in heroes_platform/"; exit 1; fi
	@if [ -f "../.env" ] && [ ! -f ".env" ]; then cp ../.env .; fi
	@echo "✅ Setup complete"

setup-mcp:
	@echo "🔧 Setting up MCP configuration..."
	@python scripts/setup_mcp_config.py
	@echo "✅ MCP configuration setup complete"

venv:
	@echo "🐍 Creating virtual environment..."
	@python -m venv .venv
	@echo "✅ Virtual environment created"

deps: venv
	@echo "📦 Installing dependencies from pyproject.toml..."
	@python setup.py
	@echo "✅ Dependencies installed"

# Testing targets
test: install-dev
	@echo "🧪 Running all tests..."
	@python -m pytest tests/ -v

test-unit: install-dev
	@echo "🧪 Running unit tests..."
	@python -m pytest tests/ -m "unit" -v

test-integration: install-dev
	@echo "🧪 Running integration tests..."
	@python -m pytest tests/ -m "integration" -v

test-coverage: install-dev
	@echo "🧪 Running tests with coverage..."
	@python -m pytest tests/ --cov=. --cov-report=html --cov-report=term --cov-fail-under=80

test-mcp-logs: install-dev
	@echo "🔍 Running MCP logs monitoring tests..."
	@python3 scripts/test_mcp_logs_monitoring.py

test-validate-outcome: install-dev
	@echo "🧪 Testing validate_actual_outcome..."
	@python -c "from heroes_mcp.src.heroes_mcp_server import validate_actual_outcome; result = validate_actual_outcome('https://github.com', take_screenshot=False); print('✅ validate_actual_outcome test passed')"

test-ci: install-dev
	@echo "🧪 Running CI test suite..."
	@python -m pytest tests/ --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=80
	@python -c "from heroes_mcp.src.heroes_mcp_server import validate_actual_outcome; result = validate_actual_outcome('https://github.com', take_screenshot=False); print('✅ validate_actual_outcome test passed')"

# Development targets
lint: install-dev
	@echo "🔍 Running linting..."
	@python -m ruff check .
	@python -m mypy . --ignore-missing-imports

format: install-dev
	@echo "🎨 Formatting code..."
	@python -m black .
	@python -m isort .

check-all: format lint test test-validate-outcome
	@echo "✅ All checks passed"

# Documentation targets
docs: install-dev
	@echo "📚 Building documentation..."
	@python docs_cli.py build

docs-serve: install-dev
	@echo "📚 Serving documentation locally..."
	@python docs_cli.py serve

docs-status: install-dev
	@echo "📊 Documentation status..."
	@python docs_cli.py status

docs-clean: install-dev
	@echo "🧹 Cleaning documentation..."
	@python docs_cli.py clean

docs-validate: docs
	@echo "🔍 Running documentation validation..."
	@python docs_cli.py validate

# Running targets
run-server: install-dev
	@echo "🚀 Starting MCP server..."
	@cd mcp_server && python run_mcp_server.py

run-tests: install-dev
	@echo "🧪 Running test suite..."
	@python run_tests.py

# Maintenance targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

clean-venv:
	@echo "🧹 Removing virtual environment..."
	@rm -rf .venv
	@echo "✅ Virtual environment removed"

# Platform-specific shortcuts
install-unix: install.sh
	@chmod +x install.sh
	@./install.sh

install-windows: install.bat
	@install.bat

# Quick setup for new projects
quick-setup:
	@echo "⚡ Quick setup for new project..."
	@make setup
	@make test
	@echo "✅ Quick setup complete"

