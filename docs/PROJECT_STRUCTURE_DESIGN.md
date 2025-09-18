# 🏗️ Проектирование структуры Heroes 1C Extractor

## 🎯 Цель реорганизации

Создать структуру проекта, соответствующую стандартам:
- **MCP Workflow Standard v2.3** - для MCP серверов и workflow
- **TDD Documentation Standard v2.5** - для тестирования и документации
- **Atomic Functions Architecture** - для атомарных операций
- **Code Quality Frameworks** - для качества кода

## 📋 JTBD-сценарии для структуры

### Big JTBD: Организованная разработка
**Когда** разработчик работает с проектом,
**Роль** разработчик,
**Хочет** найти нужные файлы и компоненты быстро,
**Закрывает потребность** в понятной структуре,
**Мы показываем** логически организованную структуру,
**Понимает** где что находится,
**Создаёт** эффективную разработку.

### Medium JTBD: TDD разработка
**Когда** разработчик создает новую функциональность,
**Роль** TDD разработчик,
**Хочет** следовать TDD циклу,
**Закрывает потребность** в тестировании,
**Мы показываем** структуру для тестов,
**Понимает** как организовать тесты,
**Создаёт** качественный код.

### Small JTBD: MCP серверы
**Когда** разработчик создает MCP сервер,
**Роль** MCP разработчик,
**Хочет** следовать FastMCP стандарту,
**Закрывает потребность** в структуре workflow,
**Мы показываем** структуру для MCP,
**Понимает** как организовать серверы,
**Создаёт** FastMCP серверы.

## 🏗️ НОВАЯ СТРУКТУРА ПРОЕКТА

```
heroes-1c-extractor/
├── 📁 .ide/                          # IDE конфигурации (НОВАЯ)
│   ├── .claude/
│   ├── .cursor/
│   ├── .gemini/
│   ├── .kiro/
│   ├── .roo/
│   ├── .taskmaster/
│   ├── .trae/
│   ├── .vscode/
│   ├── .windsurf/
│   └── .zed/
├── 📁 .github/                       # GitHub конфигурация
│   └── workflows/
├── 📁 src/                           # Исходный код (РЕОРГАНИЗОВАН)
│   ├── 📁 core/                      # Основная логика
│   │   ├── __init__.py
│   │   ├── database/                 # Работа с 1CD
│   │   │   ├── __init__.py
│   │   │   ├── reader.py             # Чтение 1CD файлов
│   │   │   ├── extractor.py          # Извлечение данных
│   │   │   └── validator.py          # Валидация данных
│   │   ├── analyzers/                # Анализ данных
│   │   │   ├── __init__.py
│   │   │   ├── document_analyzer.py  # Анализ документов
│   │   │   ├── reference_analyzer.py # Анализ справочников
│   │   │   └── blob_analyzer.py      # Анализ BLOB данных
│   │   └── exporters/                # Экспорт данных
│   │       ├── __init__.py
│   │       ├── xml_exporter.py       # XML экспорт
│   │       ├── json_exporter.py      # JSON экспорт
│   │       └── csv_exporter.py       # CSV экспорт
│   ├── 📁 mcp/                       # MCP серверы (НОВАЯ)
│   │   ├── __init__.py
│   │   ├── servers/                  # FastMCP серверы
│   │   │   ├── __init__.py
│   │   │   ├── extractor_server.py   # Сервер извлечения данных
│   │   │   ├── analyzer_server.py    # Сервер анализа данных
│   │   │   └── exporter_server.py    # Сервер экспорта данных
│   │   └── workflows/                # MCP workflow (1 workflow = 1 файл)
│   │       ├── __init__.py
│   │       ├── extract_workflow.py   # Workflow извлечения
│   │       ├── analyze_workflow.py   # Workflow анализа
│   │       └── export_workflow.py    # Workflow экспорта
│   ├── 📁 utils/                     # Утилиты
│   │   ├── __init__.py
│   │   ├── file_utils.py             # Работа с файлами
│   │   ├── data_utils.py             # Обработка данных
│   │   └── validation_utils.py       # Валидация
│   └── 📁 models/                    # Pydantic модели
│       ├── __init__.py
│       ├── database_models.py        # Модели БД
│       ├── analysis_models.py        # Модели анализа
│       └── export_models.py          # Модели экспорта
├── 📁 tests/                         # Тесты (НОВАЯ)
│   ├── __init__.py
│   ├── conftest.py                   # Pytest конфигурация
│   ├── 📁 unit/                      # Unit тесты
│   │   ├── __init__.py
│   │   ├── test_database/
│   │   ├── test_analyzers/
│   │   └── test_exporters/
│   ├── 📁 integration/               # Integration тесты
│   │   ├── __init__.py
│   │   ├── test_database_integration.py
│   │   └── test_mcp_integration.py
│   ├── 📁 e2e/                       # End-to-End тесты
│   │   ├── __init__.py
│   │   └── test_full_workflow.py
│   └── 📁 fixtures/                  # Тестовые данные
│       ├── sample_1cd/
│       └── expected_results/
├── 📁 data/                          # Данные (РЕОРГАНИЗОВАН)
│   ├── 📁 raw/                       # Исходные данные
│   │   └── 1Cv8.1CD                 # 81GB база данных
│   ├── 📁 processed/                 # Обработанные данные
│   │   ├── extracted/                # Извлеченные данные
│   │   └── analyzed/                 # Результаты анализа
│   └── 📁 exports/                   # Экспортированные данные
│       ├── xml/
│       ├── json/
│       └── csv/
├── 📁 tools/                         # Инструменты (РЕОРГАНИЗОВАН)
│   ├── 📁 onec_dtools/               # Python библиотека
│   ├── 📁 tool1cd/                   # Windows утилиты
│   ├── 📁 v8unpack/                  # C++ утилиты
│   └── 📁 temp-tool1cd/              # Тестовые файлы
├── 📁 config/                        # Конфигурация (РЕОРГАНИЗОВАН)
│   ├── docker/                       # Docker конфигурация
│   │   ├── Dockerfile.ctool1cd
│   │   └── docker-compose.yml
│   ├── scripts/                      # Скрипты
│   │   ├── setup_macos_environment.sh
│   │   ├── run_ctool1cd.sh
│   │   └── wine-ctool1cd.sh
│   ├── mcp.json                      # MCP конфигурация
│   └── pytest.ini                   # Pytest конфигурация
├── 📁 docs/                          # Документация (РЕОРГАНИЗОВАН)
│   ├── 📁 api/                       # API документация
│   │   ├── mcp_servers.md
│   │   └── workflows.md
│   ├── 📁 guides/                    # Руководства
│   │   ├── installation.md
│   │   ├── usage.md
│   │   └── development.md
│   ├── 📁 standards/                 # Стандарты
│   │   └── [standards .md]/          # Перенести сюда
│   └── 📁 reports/                   # Отчеты
│       ├── analysis_reports/
│       └── extraction_reports/
├── 📁 logs/                          # Логи (РЕОРГАНИЗОВАН)
│   ├── application.log
│   ├── mcp.log
│   └── tests.log
├── 📁 external/                      # Внешние репозитории (НОВАЯ)
│   ├── heroes-platform/              # Внешний репозиторий
│   ├── dck1c/                        # Внешний репозиторий
│   ├── tools_ui_1c/                  # Внешний репозиторий
│   └── advising_platform/            # Внешний репозиторий
├── 📁 archive/                       # Архив (СУЩЕСТВУЮЩАЯ)
│   ├── old_data/
│   └── old_scripts/
├── 📁 rules/                         # Правила (СУЩЕСТВУЮЩАЯ)
├── 📁 tasks/                         # Задачи (СУЩЕСТВУЮЩАЯ)
├── 📁 [prostocvet-1c]/              # Специальная папка (СУЩЕСТВУЮЩАЯ)
├── .gitignore                        # Git ignore
├── README.md                         # Основная документация
├── requirements.txt                  # Python зависимости
├── pyproject.toml                    # Python проект
├── docker-compose.yml                # Docker compose
└── Makefile                          # Make команды
```

## 🔧 КЛЮЧЕВЫЕ ПРИНЦИПЫ СТРУКТУРЫ

### 1. **MCP Workflow Architecture**
- **1 workflow = 1 файл** в `src/mcp/workflows/`
- **FastMCP серверы** в `src/mcp/servers/`
- **Атомарные операции** ≤20 строк
- **Pydantic модели** в `src/models/`

### 2. **TDD Testing Pyramid**
- **Unit тесты** в `tests/unit/`
- **Integration тесты** в `tests/integration/`
- **E2E тесты** в `tests/e2e/`
- **Fixtures** в `tests/fixtures/`

### 3. **Atomic Functions Architecture**
- **Публичные методы** ≤25 строк
- **Приватные методы** ≤20 строк
- **JTBD документация** для каждого компонента
- **Reflection checkpoints** в workflow

### 4. **Code Quality Frameworks**
- **Type hints** для всех функций
- **Pydantic модели** для валидации
- **Async/await** для I/O операций
- **Context managers** для ресурсов

## 📋 ПЛАН РЕОРГАНИЗАЦИИ

### Этап 1: Создание новой структуры
1. Создать папку `.ide/` и переместить IDE конфигурации
2. Создать папку `external/` и переместить внешние репозитории
3. Создать папку `tests/` с Testing Pyramid структурой
4. Создать папку `src/mcp/` для MCP серверов

### Этап 2: Реорганизация существующих файлов
1. Переместить скрипты в `src/core/`
2. Переместить конфигурацию в `config/`
3. Реорганизовать `data/` папку
4. Обновить `docs/` структуру

### Этап 3: Создание MCP серверов
1. Создать FastMCP серверы в `src/mcp/servers/`
2. Создать workflow в `src/mcp/workflows/`
3. Создать Pydantic модели в `src/models/`
4. Настроить тестирование MCP

### Этап 4: Настройка тестирования
1. Настроить pytest конфигурацию
2. Создать unit тесты
3. Создать integration тесты
4. Создать E2E тесты

### Этап 5: Документация и CI/CD
1. Создать API документацию
2. Настроить GitHub Actions
3. Создать Makefile
4. Обновить README.md

## 🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### После реорганизации:
- **Чистая структура** - логически организованные папки
- **TDD готовность** - полная структура для тестирования
- **MCP готовность** - структура для FastMCP серверов
- **Качество кода** - соответствие стандартам
- **Документация** - полная документация API
- **CI/CD** - автоматизированное тестирование

### Метрики качества:
- **Test Coverage** ≥90%
- **Code Complexity** ≤10
- **MCP Compliance** 100%
- **TDD Compliance** 100%
- **Documentation** 100%

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **Создать план реорганизации** в `1c.todo.md`
2. **Начать с создания новой структуры**
3. **Поэтапно перемещать файлы**
4. **Создавать MCP серверы**
5. **Настраивать тестирование**
6. **Обновлять документацию**

---

**Уверенность: 0.95** - Структура спроектирована на основе изученных стандартов MCP Workflow и TDD Documentation, учитывает все требования и принципы организации кода.
