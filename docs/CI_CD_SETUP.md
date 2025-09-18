# 🚀 CI/CD Setup для Notebook QA Testing

## 📋 Обзор

Автоматизированная система тестирования качества notebook с данными из 1С, основанная на AI QA стандарте.

## 🔧 Компоненты системы

### 1. Автоматизированные тесты
- **Файл**: `tests/notebook/test_notebook_qa.py`
- **Функции**:
  - Проверка синтаксиса notebook
  - Валидация данных из 1С
  - Тестирование производительности
  - Проверка метрик AI качества

### 2. GitHub Actions Workflow
- **Файл**: `.github/workflows/notebook-qa.yml`
- **Триггеры**:
  - Push в main/develop ветки
  - Pull requests
  - Изменения в notebooks/ или data/results/

### 3. Скрипт запуска тестов
- **Файл**: `scripts/run_notebook_qa.py`
- **Функции**:
  - Локальный запуск тестов
  - Проверка файлов данных
  - Тестирование выполнения notebook

### 4. Makefile
- **Файл**: `Makefile`
- **Команды**:
  - `make test-notebook` - тесты notebook
  - `make test-qa` - тесты качества
  - `make test-all` - все тесты
  - `make quality-report` - отчет о качестве

## 🎯 Тест-кейсы по AI QA стандарту

### Test Case 1: Syntax Error Detection
- **WHO**: CI/CD система
- **WHAT**: Обнаружение синтаксических ошибок в f-string
- **WHEN**: При каждом коммите
- **WHERE**: GitHub Actions
- **WHY**: Предотвращение блокировки отображения данных
- **HOW**: Автоматический анализ кода + pytest

### Test Case 2: Data Quality Validation
- **WHO**: CI/CD система
- **WHAT**: Проверка качества данных из 1С
- **WHEN**: При изменении данных
- **WHERE**: GitHub Actions
- **WHY**: Убедиться в корректности данных
- **HOW**: Pandas + DuckDB валидация

### Test Case 3: Performance Testing
- **WHO**: CI/CD система
- **WHAT**: Проверка производительности загрузки данных
- **WHEN**: При каждом тесте
- **WHERE**: GitHub Actions
- **WHY**: Обеспечить быструю работу
- **HOW**: Измерение времени загрузки

### Test Case 4: AI Metrics Validation
- **WHO**: CI/CD система
- **WHAT**: Проверка метрик AI качества
- **WHEN**: При каждом тесте
- **WHERE**: GitHub Actions
- **WHY**: Соответствие AI QA стандарту
- **HOW**: Автоматический расчет метрик

## 🚀 Запуск тестов

### Локальный запуск
```bash
# Все тесты
make test-all

# Только тесты notebook
make test-notebook

# Только тесты качества
make test-qa

# Проверка данных
make check-data

# Отчет о качестве
make quality-report
```

### Через скрипт
```bash
# Все тесты
python scripts/run_notebook_qa.py --type all --verbose

# Только синтаксис
python scripts/run_notebook_qa.py --type syntax

# Только данные
python scripts/run_notebook_qa.py --type data

# Проверка файлов
python scripts/run_notebook_qa.py --check-data

# Тест выполнения
python scripts/run_notebook_qa.py --test-execution
```

### Через pytest
```bash
# Все тесты
pytest tests/notebook/test_notebook_qa.py -v

# Только тесты качества
pytest tests/notebook/test_notebook_qa.py::TestNotebookAIMetrics -v

# С покрытием
pytest tests/notebook/test_notebook_qa.py --cov=notebooks --cov-report=html
```

## 📊 Метрики качества

### Количественные метрики
1. **Точность (Accuracy)**: >95%
2. **Время загрузки**: <5 секунд
3. **Полнота данных**: 100% для обязательных полей
4. **Консистентность**: 100% между Parquet и DuckDB

### Качественные метрики
1. **Отсутствие синтаксических ошибок**: 100%
2. **Корректность отображения данных**: 100%
3. **Производительность**: <5 секунд
4. **Соответствие AI QA стандарту**: 100%

## 🔍 Мониторинг

### GitHub Actions
- Автоматический запуск при push/PR
- Отчеты о результатах тестов
- Артефакты с результатами
- Комментарии в PR с результатами

### Локальный мониторинг
```bash
# Проверка статуса
make check

# Полная проверка
make ci

# Отчет о качестве
make quality-report
```

## 🛠️ Настройка

### 1. Установка зависимостей
```bash
make install
```

### 2. Настройка GitHub Actions
- Файл уже создан: `.github/workflows/notebook-qa.yml`
- Автоматически запускается при push/PR

### 3. Настройка pytest
- Конфигурация: `pytest.ini`
- Маркеры для разных типов тестов
- Настройки покрытия

## 📈 Отчеты

### Автоматические отчеты
- GitHub Actions logs
- Артефакты с результатами
- Комментарии в PR

### Локальные отчеты
```bash
# Отчет о качестве
make quality-report

# HTML отчет покрытия
pytest --cov=notebooks --cov-report=html
```

## 🔧 Troubleshooting

### Частые проблемы

1. **Файлы данных не найдены**
   ```bash
   make check-data
   ```

2. **Синтаксические ошибки**
   ```bash
   make test-syntax
   ```

3. **Проблемы с производительностью**
   ```bash
   make test-performance
   ```

4. **Ошибки в notebook**
   ```bash
   make test-execution
   ```

### Логи и отладка
```bash
# Подробные логи
python scripts/run_notebook_qa.py --type all --verbose

# Отладка pytest
pytest tests/notebook/test_notebook_qa.py -v -s

# Проверка файлов
ls -la data/results/parquet/
ls -la data/results/duckdb/
```

## 📚 Дополнительные ресурсы

- [AI QA Standard](standards%20.md/4.%20dev%20·%20design%20·%20qa/1.2%20ai%20qa%20standard%2014%20may%202025%200550%20cet%20by%20ai%20assistant.md)
- [Notebook Documentation](notebooks/parquet_analysis.ipynb)
- [Test Cases](tests/notebook/test_notebook_qa.py)
- [GitHub Actions](.github/workflows/notebook-qa.yml)

## 🎯 Следующие шаги

1. **Настройка уведомлений**: Slack/Email при ошибках
2. **Расширение тестов**: Добавление новых тест-кейсов
3. **Мониторинг**: Настройка дашбордов
4. **Автоматизация**: Автоматическое исправление ошибок
