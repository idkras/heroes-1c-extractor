# CocoIndex Workflow

## JTBD (Job To Be Done)

**Как AI Agent, я хочу искать существующие скрипты через CocoIndex, чтобы избежать дублирования кода и использовать уже существующие решения.**

## Стандарт

- **Стандарт**: TDD Documentation Standard v2.5
- **Принцип**: 1 workflow = 1 файл, атомарные функции ≤20 строк
- **Архитектура**: Модульная с четким разделением ответственности

## Архитектура

### Основные компоненты

1. **CocoIndexWorkflow** - основной класс workflow
2. **MCP функции-прокси** - интерфейс для MCP сервера
3. **Unit тесты** - полное покрытие тестами
4. **Интеграционные тесты** - проверка end-to-end сценариев

### Структура файлов

```
workflows/
├── cocoindex_workflow.py          # Основной workflow
tests/
├── unit/
│   └── test_cocoindex_workflow.py # Unit тесты
docs/
└── workflows/
    └── cocoindex_workflow.md      # Документация
```

## Функциональность

### 1. Поиск существующих файлов

**JTBD**: Как поисковая система, я хочу найти существующие файлы по запросу, чтобы предотвратить дублирование кода.

**Функция**: `search_existing_files(query: str, confidence_threshold: float = 0.6)`

**Параметры**:
- `query` - поисковый запрос
- `confidence_threshold` - минимальный уровень уверенности (по умолчанию 0.6)

**Возвращает**:
```json
{
  "query": "поисковый запрос",
  "results": [
    {
      "file": "путь к файлу",
      "type": "тип файла",
      "relevance": 0.9,
      "reason": "причина релевантности"
    }
  ],
  "confidence": 0.9,
  "recommendation": "рекомендация",
  "total_found": 5
}
```

### 2. Валидация создания файлов

**JTBD**: Как валидатор создания файлов, я хочу проверить необходимость создания файла, чтобы предотвратить дублирование функциональности.

**Функция**: `validate_file_creation(file_path: str, content: str)`

**Параметры**:
- `file_path` - путь к создаваемому файлу
- `content` - содержимое файла

**Возвращает**:
```json
{
  "should_create": true,
  "confidence": 0.3,
  "content_analysis": {
    "confidence": 0.3,
    "analysis": "описание анализа"
  },
  "project_analysis": {
    "confidence": 0.5,
    "analysis": "описание анализа структуры"
  },
  "recommendation": "Safe to create"
}
```

### 3. Карта функциональности

**JTBD**: Как картограф функциональности, я хочу создать карту существующих возможностей, чтобы AI Agent понимал архитектуру проекта.

**Функция**: `get_functionality_map()`

**Возвращает**:
```json
{
  "functionality_map": {
    "workflows": ["список workflow файлов"],
    "tests": ["список тестовых файлов"],
    "integrations": ["список интеграционных файлов"],
    "utilities": ["список утилитарных файлов"],
    "documentation": ["список документации"]
  },
  "statistics": {
    "workflows": 5,
    "tests": 10,
    "integrations": 3,
    "utilities": 8,
    "documentation": 2
  },
  "total_files": 28,
  "key_scripts_count": 15
}
```

### 4. Анализ дублирования

**JTBD**: Как анализатор дублирования, я хочу выявить дублирующийся код, чтобы оптимизировать архитектуру проекта.

**Функция**: `analyze_duplicates()`

**Возвращает**:
```json
{
  "duplicates": [
    {
      "type": "filename_duplicate",
      "files": ["файл1", "файл2"],
      "severity": "medium"
    }
  ],
  "total_duplicates": 3,
  "analysis_date": "2025-01-27 12:00:00",
  "recommendations": [
    "Found 3 potential duplicates",
    "Consider renaming files with duplicate names"
  ]
}
```

## MCP Интеграция

### Функции-прокси

Все функции workflow доступны через MCP сервер через функции-прокси:

1. **cocoindex_search** - поиск существующих файлов
2. **cocoindex_validate_creation** - валидация создания файлов
3. **cocoindex_functionality_map** - карта функциональности
4. **cocoindex_analyze_duplicates** - анализ дублирования

### Пример использования

```python
# Поиск существующих файлов
result = cocoindex_search("telegram integration", 0.7)

# Валидация создания нового файла
validation = cocoindex_validate_creation(
    "workflows/telegram_workflow.py",
    "def telegram_integration():\n    pass"
)

# Получение карты функциональности
functionality_map = cocoindex_functionality_map()

# Анализ дублирования
duplicates = cocoindex_analyze_duplicates()
```

## Тестирование

### Unit тесты

Полное покрытие unit тестами всех функций workflow:

- **24 теста** покрывают все основные функции
- **2 интеграционных теста** проверяют end-to-end сценарии
- **100% покрытие** критических путей выполнения

### Запуск тестов

```bash
# Запуск всех тестов
python -m pytest tests/unit/test_cocoindex_workflow.py -v

# Запуск с покрытием
python -m pytest tests/unit/test_cocoindex_workflow.py --cov=workflows.cocoindex_workflow
```

### Тестовые сценарии

1. **Инициализация workflow** - проверка корректной загрузки данных
2. **Поиск файлов** - валидные и невалидные запросы
3. **Валидация создания** - существующие и новые файлы
4. **Анализ содержимого** - проверка алгоритмов анализа
5. **Категоризация файлов** - проверка логики категоризации
6. **Анализ дублирования** - выявление различных типов дубликатов

## Конфигурация

### Пути к файлам

```python
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
PYTHON_FILES_INDEX = PROJECT_ROOT / "data/indices/python_files_index.txt"
COCOINDEX_BASIC_INDEX = PROJECT_ROOT / "data/indices/cocoindex_basic_index.txt"
DUPLICATE_ANALYSIS_REPORT = PROJECT_ROOT / "docs/reports/duplicate_analysis_report.md"
FUNCTIONALITY_MAP_REPORT = PROJECT_ROOT / "docs/reports/functionality_map_report.md"
```

### Фильтрация файлов

- Исключение файлов из `venv` и `.venv` директорий
- Приоритетный поиск по ключевым скриптам
- Категоризация по типам файлов

## Принципы проектирования

### 1. Атомарность функций

Каждая функция выполняет одну конкретную задачу и не превышает 20 строк кода.

### 2. JTBD-ориентированность

Все функции имеют четко определенные JTBD (Job To Be Done) для понимания назначения.

### 3. Обработка ошибок

Все функции включают try-catch блоки для graceful обработки ошибок.

### 4. Логирование

Использование стандартного Python logging для отслеживания выполнения.

### 5. Типизация

Полная типизация всех функций с использованием type hints.

## Интеграция с основным MCP сервером

### Импорт в mcp_server.py

```python
from workflows.cocoindex_workflow import (
    cocoindex_search,
    cocoindex_validate_creation,
    cocoindex_functionality_map,
    cocoindex_analyze_duplicates
)
```

### Регистрация MCP инструментов

```python
@mcp.tool()
def cocoindex_search_tool(query: str, confidence_threshold: float = 0.6) -> str:
    """Поиск существующих скриптов через CocoIndex"""
    return cocoindex_search(query, confidence_threshold)

@mcp.tool()
def cocoindex_validate_creation_tool(file_path: str, content: str) -> str:
    """Валидация создания нового файла"""
    return cocoindex_validate_creation(file_path, content)

@mcp.tool()
def cocoindex_functionality_map_tool() -> str:
    """Получить карту функциональности проекта"""
    return cocoindex_functionality_map()

@mcp.tool()
def cocoindex_analyze_duplicates_tool() -> str:
    """Анализ дублирований в проекте"""
    return cocoindex_analyze_duplicates()
```

## Мониторинг и метрики

### Ключевые метрики

1. **Время выполнения поиска** - должно быть < 100ms
2. **Точность поиска** - confidence level для релевантных результатов
3. **Количество предотвращенных дубликатов** - статистика использования
4. **Покрытие тестами** - должно быть 100%

### Логирование

```python
logger = logging.getLogger(__name__)
logger.info(f"Search completed: {query} -> {len(results)} results")
logger.warning(f"Potential duplicate detected: {file_path}")
logger.error(f"Search failed: {error}")
```

## Будущие улучшения

### Планируемые функции

1. **Семантический поиск** - поиск по содержимому файлов
2. **Машинное обучение** - улучшение алгоритмов релевантности
3. **Кэширование результатов** - оптимизация производительности
4. **Интеграция с Git** - анализ истории изменений
5. **Визуализация зависимостей** - графическое представление связей

### Оптимизации

1. **Асинхронная обработка** - для больших проектов
2. **Индексирование** - предварительная обработка файлов
3. **Параллельный поиск** - использование многопоточности
4. **Сжатие данных** - оптимизация хранения индексов

## Заключение

CocoIndex Workflow предоставляет надежную и масштабируемую систему для поиска и анализа существующих файлов в проекте. Следование принципам TDD обеспечивает высокое качество кода и полное покрытие тестами.

Workflow интегрирован с MCP сервером и готов к использованию AI агентами для предотвращения дублирования кода и оптимизации архитектуры проекта.
