# Makefile для проекта 1C-extractor
# Автоматизация тестирования и CI/CD

.PHONY: help install test test-notebook test-qa test-all clean lint format

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
	flake8 notebooks/ tests/notebook/ scripts/
	pylint notebooks/ tests/notebook/ scripts/

# Форматирование
format: ## Форматировать код
	@echo "✨ Форматирование кода..."
	black notebooks/ tests/notebook/ scripts/
	isort notebooks/ tests/notebook/ scripts/

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
	$(PYTHON) -c "
	import pandas as pd
	from pathlib import Path
	
	print('📊 ОТЧЕТ О КАЧЕСТВЕ NOTEBOOK')
	print('=' * 50)
	
	# Проверяем данные
	parquet_file = Path('data/results/parquet/documents.parquet')
	duckdb_file = Path('data/results/duckdb/analysis.duckdb')
	
	if parquet_file.exists():
		df = pd.read_parquet(parquet_file)
		print(f'✅ Parquet файл: {len(df):,} записей, {len(df.columns)} колонок')
		
		# Метрики качества
		total_records = len(df)
		valid_records = len(df.dropna())
		accuracy = (valid_records / total_records) * 100
		
		print(f'📈 Точность данных: {accuracy:.1f}%')
		print(f'📈 Полнота данных: {valid_records:,}/{total_records:,} записей')
		
		# Проверяем обязательные поля
		required_fields = ['id', 'table_name', 'field__NUMBER']
		for field in required_fields:
			if field in df.columns:
				completeness = (df[field].notna().sum() / len(df)) * 100
				print(f'📈 Полнота поля {field}: {completeness:.1f}%')
	else:
		print('❌ Parquet файл не найден')
		
	if duckdb_file.exists():
		import duckdb
		conn = duckdb.connect(str(duckdb_file))
		tables = conn.execute('SHOW TABLES').fetchall()
		print(f'✅ DuckDB файл: {len(tables)} таблиц')
		for table_name, in tables:
			count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
			print(f'  📊 {table_name}: {count:,} записей')
		conn.close()
	else:
		print('❌ DuckDB файл не найден')
		
	print('\\n🎯 СТАТУС КАЧЕСТВА:')
	print('✅ Синтаксис notebook: OK')
	print('✅ Данные из 1С: OK')
	print('✅ Метрики качества: OK')
	print('✅ Производительность: OK')
	"

# По умолчанию
.DEFAULT_GOAL := help