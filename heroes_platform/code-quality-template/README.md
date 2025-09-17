# Шаблон системы качества кода Python

Этот шаблон содержит полную настройку автоматизации качества кода для Python проектов, включая линтеры, форматирование, проверку типов и интеграцию с VS Code/Cursor.

## 🚀 Быстрая установка

### 1. Копирование файлов

Скопируйте все файлы из этого шаблона в корень вашего проекта:

```bash
# Скопируйте все файлы в корень проекта
cp -r code-quality-template/* /path/to/your/project/
```

### 2. Установка зависимостей

```bash
# Установка development зависимостей
pip install -r requirements-dev.txt

# Или через make (если доступен)
make setup
```

### 3. Настройка pre-commit

```bash
# Установка pre-commit хуков
pre-commit install
```

### 4. Проверка установки

```bash
# Запуск всех проверок
make check

# Или по отдельности
make lint
make format
make test
```

## 📁 Структура файлов

```
code-quality-template/
├── CODE_QUALITY_AUTOMATION.md    # Документация системы
├── pyproject.toml                # Конфигурация всех инструментов
├── .pre-commit-config.yaml       # Pre-commit хуки
├── Makefile                      # Команды для разработки
├── requirements-dev.txt          # Development зависимости
├── .vscode/
│   ├── settings.json            # Настройки VS Code
│   └── tasks.json               # Задачи VS Code
├── scripts/
│   └── ruff_monitor.py          # Автоматический мониторинг
└── .cursor/
    ├── mcp-enhanced.json        # Конфигурация Cursor
    └── rules/
        ├── cursor_rules.mdc     # Правила Cursor
        ├── dev_workflow.mdc     # Рабочий процесс
        └── self_improve.mdc     # Самоулучшение
```

## 🛠️ Настройка для вашего проекта

### 1. Обновите pyproject.toml

Измените следующие секции в `pyproject.toml`:

```toml
[project]
name = "your-project-name"
version = "1.0.0"
description = "Your project description"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

# Обновите зависимости под ваш проект
dependencies = [
    # Ваши зависимости
]

[tool.mypy]
# Обновите исключения под вашу структуру проекта
exclude = [
    "your_project/tests/.*",
    "your_project/migrations/.*",
]
```

### 2. Настройте .gitignore

Добавьте в `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/settings.json
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Linting
.ruff_cache/
.mypy_cache/

# Reports
bandit-report.json
```

### 3. Настройте VS Code

Убедитесь, что у вас установлены расширения VS Code:
- Python
- Ruff
- Black Formatter
- MyPy Type Checker

## 🔧 Доступные команды

### Make команды

```bash
make help          # Показать все команды
make setup         # Установка dev зависимостей + pre-commit
make install       # Установка production зависимостей
make install-dev   # Установка development зависимостей
make test          # Запуск тестов с покрытием
make test-fast     # Запуск тестов без покрытия
make lint          # Запуск всех линтеров
make format        # Форматирование кода
make check         # Полная проверка (формат + линт + тесты)
make clean         # Очистка cache файлов
make ruff-check    # Только проверка Ruff
make ruff-fix      # Авто-исправление Ruff
make ruff-watch    # Запуск фонового мониторинга
make qa-ruff       # QA цикл с Ruff
```

### VS Code задачи

В VS Code (Ctrl+Shift+P → "Tasks: Run Task"):
- **Ruff Watch (workspace)** - фоновый мониторинг
- **Ruff Fix All** - исправление всех проблем
- **Ruff Format All** - форматирование всех файлов

### Прямые команды

```bash
# Ruff
ruff check .              # Проверка
ruff check . --fix        # Проверка с авто-исправлением
ruff format .             # Форматирование

# MyPy
mypy .                    # Проверка типов

# Black
black .                   # Форматирование

# Bandit
bandit -r .               # Проверка безопасности

# Safety
safety check              # Проверка уязвимостей

# Pre-commit
pre-commit run --all-files # Запуск всех хуков
```

## 🚨 Автоматические проверки

### Pre-commit хуки (при каждом коммите)
- Black - форматирование
- Ruff - линтинг
- MyPy - проверка типов
- Bandit - безопасность
- Safety - уязвимости зависимостей

### VS Code (в реальном времени)
- Ruff lint при наборе
- Авто-форматирование при сохранении
- Проверка типов

### Автоматический мониторинг
```bash
python scripts/ruff_monitor.py
```

## 📊 Отчеты и метрики

### Отчеты
- **Bandit:** `bandit-report.json`
- **Coverage:** `htmlcov/` директория
- **Ruff:** Консольный вывод
- **MyPy:** Консольный вывод

### Цели качества
- **Покрытие тестами:** >80%
- **Проблемы линтера:** 0
- **Проблемы типов:** 0
- **Проблемы безопасности:** 0

## 🔄 CI/CD интеграция

### GitHub Actions

Создайте `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-dev.txt
      - run: pre-commit install
      - run: make check
```

## 🎯 Результат

После установки вы получите:

1. **Автоматическое форматирование** кода при сохранении
2. **Проверку в реальном времени** ошибок линтера
3. **Блокировку коммитов** с проблемами качества
4. **Строгую проверку типов** для предотвращения ошибок
5. **Проверку безопасности** кода
6. **Интеграцию с AI агентами** (Cursor)

## 📚 Дополнительная документация

- [CODE_QUALITY_AUTOMATION.md](CODE_QUALITY_AUTOMATION.md) - подробная документация системы
- [DEVELOPMENT.md](DEVELOPMENT.md) - руководство по разработке

## 🆘 Устранение проблем

### Ruff не найден
```bash
pip install ruff
```

### Pre-commit не работает
```bash
pre-commit install
pre-commit run --all-files
```

### MyPy ошибки
```bash
# Добавьте типы в код или настройте исключения в pyproject.toml
mypy . --ignore-missing-imports
```

### VS Code не показывает проблемы
1. Убедитесь, что установлено расширение Ruff
2. Перезапустите VS Code
3. Проверьте настройки в `.vscode/settings.json`
