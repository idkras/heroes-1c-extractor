# Makefile for MCP Server Quality Management

.PHONY: help install dev-install format lint type-check test test-cov clean pre-commit install-hooks

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -e .

dev-install: ## Установить зависимости для разработки
	pip install -e ".[dev]"

format: ## Форматировать код
	ruff format .
	black .

lint: ## Проверить код линтером
	ruff check .
	ruff check --fix .

type-check: ## Проверить типы
	mypy src/ tests/

test: ## Запустить тесты
	pytest

test-cov: ## Запустить тесты с покрытием
	pytest --cov=src --cov-report=html --cov-report=term-missing

clean: ## Очистить кэш и временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

pre-commit: ## Запустить pre-commit на всех файлах
	pre-commit run --all-files

install-hooks: ## Установить pre-commit хуки
	pre-commit install

check-all: format lint type-check test ## Запустить все проверки

# API Documentation
docs-generate: ## Генерировать API документацию
	@echo "📚 Generating API documentation..."
	python scripts/generate_api_docs.py

docs-serve: ## Запустить веб-сервер для просмотра документации
	@echo "🌐 Serving API documentation..."
	cd docs/api && python -m http.server 8080

docs-validate: ## Валидировать API документацию
	@echo "✅ Validating API documentation..."
	@python3 -c "import json; from pathlib import Path; spec_path = Path('docs/api/openapi.json'); spec = json.load(open(spec_path)) if spec_path.exists() else None; print(f'✅ OpenAPI spec valid: {len(spec.get(\"paths\", {}))} endpoints') if spec else print('❌ OpenAPI spec not found') or exit(1)"

setup: dev-install install-hooks ## Полная настройка проекта
