.PHONY: help install install-dev test lint format check clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

test: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage
	pytest tests/ -v

lint: ## Run all linting tools
	ruff check .
	bandit -r . --skip B607,B101
	safety check

format: ## Format code with Black and Ruff
	black .
	ruff check --fix .

check: ## Run all checks (format, lint, test)
	black --check .
	ruff check .
	bandit -r . --skip B607,B101
	safety check
	pytest tests/ --cov=src --cov-report=term-missing

clean: ## Clean up cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/

setup: install-dev ## Setup development environment
	pre-commit install
	@echo "Development environment setup complete!"

# Ruff Quality Assurance
ruff-check:
	@echo "🔍 Проверка качества кода с Ruff..."
	ruff check .

ruff-fix:
	@echo "🔧 Автоматическое исправление проблем с Ruff..."
	ruff check . --fix
	ruff format .

ruff-watch:
	@echo "👀 Запуск фонового мониторинга Ruff..."
	@if command -v code >/dev/null 2>&1; then \
		code --command "workbench.action.tasks.runTask" --args "Ruff Watch (workspace)"; \
	else \
		echo "VS Code не найден. Запускаю Python скрипт..."; \
		python scripts/ruff_monitor.py; \
	fi

ruff-monitor:
	@echo "🤖 Запуск автоматического мониторинга..."
	python scripts/ruff_monitor.py

qa-ruff: ruff-fix ruff-check
	@echo "✅ QA цикл завершен"
