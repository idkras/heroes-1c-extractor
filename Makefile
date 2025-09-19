# Makefile для проекта 1C-extractor
# Автоматизация тестирования и CI/CD

.PHONY: help install test test-notebook test-qa test-all clean lint format fix-linter auto-fix

# Переменные
PYTHON := python3
PIP := pip3
PYTEST := pytest
NOTEBOOK_TESTS := tests/notebook/test_notebook_qa.py
QA_SCRIPT := scripts/run_notebook_qa.py

# Помощь
help: ## Показать справку
	@echo "🔍 NOTEBOOK QA TESTING - Справка"
	@echo "================================"
	@echo ""
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Установка зависимостей
install: ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov nbformat nbconvert

# Тестирование notebook
test-notebook: ## Запустить тесты notebook
	@echo "🧪 Запуск тестов notebook..."
	$(PYTHON) $(QA_SCRIPT) --type all --verbose

# Тестирование качества
test-qa: ## Запустить тесты качества
	@echo "🔍 Запуск тестов качества..."
	$(PYTHON) $(QA_SCRIPT) --type ai_metrics --verbose

# Тестирование данных
test-data: ## Запустить тесты данных
	@echo "📊 Запуск тестов данных..."
	$(PYTHON) $(QA_SCRIPT) --type data --verbose

# Тестирование производительности
test-performance: ## Запустить тесты производительности
	@echo "⚡ Запуск тестов производительности..."
	$(PYTHON) $(QA_SCRIPT) --type performance --verbose

# Тестирование синтаксиса
test-syntax: ## Запустить тесты синтаксиса
	@echo "🔤 Запуск тестов синтаксиса..."
	$(PYTHON) $(QA_SCRIPT) --type syntax --verbose

# Все тесты
test-all: ## Запустить все тесты
	@echo "🎯 Запуск всех тестов..."
	$(PYTHON) $(QA_SCRIPT) --type all --check-data --test-execution --verbose

# Проверка файлов данных
check-data: ## Проверить файлы данных
	@echo "🔍 Проверка файлов данных..."
	$(PYTHON) $(QA_SCRIPT) --check-data

# Тест выполнения notebook
test-execution: ## Тестировать выполнение notebook
	@echo "▶️ Тестирование выполнения notebook..."
	$(PYTHON) $(QA_SCRIPT) --test-execution

# Линтинг
lint: ## Запустить линтер
	@echo "🔍 Запуск линтера..."
	python3 -m flake8 src/ tests/
	python3 -m mypy src/ tests/

# Форматирование
format: ## Форматировать код
	@echo "✨ Форматирование кода..."
	python3 -m black src/ tests/
	python3 -m isort src/ tests/

fix-linter: ## Исправить ошибки линтера автоматически
	@echo "🔧 Автоматическое исправление ошибок линтера..."
	@source .venv/bin/activate && python scripts/fix_linter_errors.py
	@echo "✅ Ошибки линтера исправлены"

auto-fix: fix-linter format ## Полное автоисправление (линтер + форматирование)
	@echo "🚀 Полное автоисправление завершено"

# Очистка
clean: ## Очистить временные файлы
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage

# Полная проверка
check: install test-all lint ## Полная проверка проекта
	@echo "✅ Полная проверка завершена!"

# CI/CD проверка
ci: install test-all ## Проверка для CI/CD
	@echo "🚀 CI/CD проверка завершена!"

# Отчет о качестве
quality-report: ## Генерация отчета о качестве
	@echo "📊 Генерация отчета о качестве..."
	$(PYTHON) scripts/run_notebook_qa.py --type ai_metrics

# По умолчанию
.DEFAULT_GOAL := help
