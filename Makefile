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

# Pre-commit установка
install-pre-commit: ## Установить pre-commit хуки
	@echo "📦 Установка pre-commit хуков..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-commit хуки установлены"

# Линтинг
lint: ## Запустить линтер
	@echo "🔍 Запуск линтера..."
	python3 -m flake8 src/ tests/
	python3 -m mypy src/ tests/

# Pre-commit проверки
pre-commit: ## Запустить pre-commit проверки
	@echo "🔍 Запуск pre-commit проверок..."
	pre-commit run --all-files

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

# DeepSource локальная проверка
deepsource-local: pre-commit lint ## Локальная проверка DeepSource
	@echo "🔍 Локальная проверка DeepSource..."
	@echo "✅ Все проверки пройдены локально"

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

# SonarQube анализ
sonar-local: ## Запустить локальный анализ SonarQube
	@echo "🔍 Запуск локального анализа SonarQube..."
	docker-compose -f docker-compose.sonarqube.yml up -d sonarqube sonarqube-db
	@echo "⏳ Ожидание запуска SonarQube (30 секунд)..."
	sleep 30
	@echo "🌐 SonarQube доступен по адресу: http://localhost:9000"
	@echo "🔑 Логин: admin, Пароль: admin"

sonar-scan: ## Запустить сканирование кода SonarQube
	@echo "🔍 Запуск сканирования кода..."
	docker-compose -f docker-compose.sonarqube.yml run --rm sonar-scanner

sonar-stop: ## Остановить SonarQube
	@echo "🛑 Остановка SonarQube..."
	docker-compose -f docker-compose.sonarqube.yml down

sonar-clean: ## Очистить данные SonarQube
	@echo "🧹 Очистка данных SonarQube..."
	docker-compose -f docker-compose.sonarqube.yml down -v
	docker volume prune -f

# Безопасность
security-scan: ## Запустить сканирование безопасности
	@echo "🔒 Запуск сканирования безопасности..."
	bandit -r src/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "✅ Отчеты безопасности сохранены: bandit-report.json, safety-report.json"

# Полная проверка качества
quality-check: test-all lint security-scan ## Полная проверка качества кода
	@echo "🎯 Полная проверка качества завершена!"

# По умолчанию
.DEFAULT_GOAL := help
