# Heroes MCP Server

MCP сервер для работы со стандартами и инструментами, интегрированный с Cursor.
Использует FastMCP для быстрой разработки MCP инструментов.
Включает интеграцию с Telegram через Mac Keychain.

## Установка и настройка

### 1. Создание виртуального окружения

```bash
cd heroes-platform/heroes-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка в Cursor IDE

В настройках Cursor IDE (Cursor Settings) в разделе "Tools & Integrations" > "MCP Tools":

1. Найдите сервер "heroes-mcp"
2. Измените путь на: `/Users/ilyakrasinsky/workspace/vscode.projects/heroes-template/heroes-platform/heroes-mcp/src/heroes-mcp.py`
3. Убедитесь, что переключатель включен (зеленый)

### 3. Проверка работы

```bash
# Тестовый режим
python3 src/heroes-mcp.py --test

# Запуск сервера
python3 src/heroes-mcp.py
```

## Доступные инструменты

### Основные команды
- `server_info` - Информация о сервере
- `standards_management` - Управление стандартами проекта
- `heroes_gpt_workflow` - HeroesGPT workflow для анализа
- `performance_monitor` - Мониторинг производительности

### Telegram интеграция
- `telegram_get_credentials` - Получение учетных данных Telegram из Mac Keychain
- `telegram_test_connection` - Тестирование подключения к Telegram
- `telegram_get_chats` - Получение списка чатов Telegram
- `telegram_search_chats` - Поиск чатов Telegram
- `telegram_export_chat` - Экспорт истории чата

### CocoIndex интеграция
- `cocoindex_search_existing_files` - Поиск существующих файлов
- `cocoindex_validate_file_creation` - Валидация создания файлов
- `cocoindex_get_functionality_map` - Карта функциональности
- `cocoindex_analyze_duplicates` - Анализ дублирований

### n8n интеграция
- `n8n_init_integration` - Инициализация интеграции с n8n
- `n8n_health_check` - Проверка состояния n8n сервера
- `n8n_list_workflows` - Список workflow
- `n8n_get_workflow` - Получение workflow по ID
- `n8n_create_workflow` - Создание нового workflow
- `n8n_update_workflow` - Обновление workflow
- `n8n_delete_workflow` - Удаление workflow
- `n8n_activate_workflow` - Активация workflow
- `n8n_deactivate_workflow` - Деактивация workflow
- `n8n_trigger_workflow` - Запуск workflow через webhook
- `n8n_get_executions` - Список выполнений
- `n8n_get_execution` - Получение выполнения по ID

## Универсальная команда анализа gap

### `analyze_output_gap`

**JTBD**: Как универсальный gap analyzer, я хочу анализировать различия между ожидаемым и фактическим output, чтобы обеспечить единый интерфейс для всех типов валидации и gap analysis.

**Параметры:**
- `expected` (str, опционально): Ожидаемый результат (строка)
- `actual` (str, опционально): Фактический результат (строка)
- `expected_file` (str, опционально): Путь к файлу с ожидаемым результатом
- `actual_file` (str, опционально): Путь к файлу с фактическим результатом
- `url` (str, опционально): URL для анализа (если анализируем веб-страницу)
- `todo_file` (str, опционально): Путь к *.todo.md файлу для извлечения критериев
- `release_name` (str, опционально): Название релиза (для todo валидации)
- `analysis_type` (str, по умолчанию "comprehensive"): Тип анализа (basic, comprehensive, strict, guidance)
- `gap_threshold` (float, по умолчанию 0.3): Порог для критических gap
- `take_screenshot` (bool, по умолчанию True): Создавать скриншот для URL
- `create_incident` (bool, по умолчанию False): Создавать инцидент при критических gap

**Возвращает:** JSON строку с унифицированным анализом gap

**Особенности:**
- Объединяет функциональность всех команд валидации и gap analysis
- Автоматически определяет тип анализа на основе входных данных
- Выполняет URL анализ, валидацию файлов, todo валидацию, gap analysis, quality validation, cross-check
- Создает инциденты при критических gap
- Предоставляет единый score и рекомендации

**Примеры использования:**

```python
# Анализ по URL
result = await analyze_output_gap(url="https://example.com")

# Анализ файлов
result = await analyze_output_gap(
    expected_file="expected.md",
    actual_file="actual.md"
)

# Анализ с todo валидацией
result = await analyze_output_gap(
    todo_file="project.todo.md",
    release_name="v1.0",
    actual_file="output.md"
)

# Полный анализ с созданием инцидента
result = await analyze_output_gap(
    expected="Ожидаемый контент",
    actual="Фактический контент",
    analysis_type="strict",
    create_incident=True
)
```

**Структура результата:**
```json
{
  "analysis_id": "GAP_20241201_143022",
  "analysis_type": "comprehensive",
  "timestamp": 1701441022.123,
  "sources": {
    "url": {...},
    "expected_file": {...},
    "actual_file": {...},
    "todo_validation": {...}
  },
  "gap_analysis": {...},
  "quality_validation": {...},
  "cross_check": {...},
  "recommendations": [...],
  "overall_gap_score": 0.85,
  "overall_assessment": "Good",
  "incident_created": false
}
```

## Структура файлов

```
heroes-platform/heroes-mcp/
├── src/
│   └── heroes-mcp.py      # Основной MCP сервер
├── venv/                  # Виртуальное окружение
├── requirements.txt       # Зависимости
└── README.md              # Этот файл
```

## Устранение неполадок

### Проблема с импортом MCP

Если возникает ошибка `ModuleNotFoundError: No module named 'mcp'`:

1. Убедитесь, что виртуальное окружение активировано
2. Переустановите MCP: `pip install --force-reinstall mcp`

### Проблема с attr/attrs

Если возникает конфликт между `attr` и `attrs`:

1. Удалите конфликтующие пакеты: `pip uninstall attr attrs -y`
2. Установите только `attrs`: `pip install attrs`
3. Переустановите MCP: `pip install --force-reinstall mcp`

### Проблема с Telegram интеграцией

1. Убедитесь, что учетные данные сохранены в Mac Keychain
2. Проверьте подключение: `telegram_test_connection`
3. При необходимости обновите учетные данные в Keychain

### Проблема с n8n интеграцией

1. Убедитесь, что n8n сервер запущен и доступен
2. Проверьте конфигурацию в `config/n8n_config.json`
3. Инициализируйте интеграцию: `n8n_init_integration`
4. Проверьте состояние: `n8n_health_check`

## Разработка

Для добавления новых инструментов:

1. Отредактируйте `src/heroes-mcp.py`
2. Добавьте новые функции с декоратором `@mcp.tool()`
3. Протестируйте: `python3 src/heroes-mcp.py --test`
4. Перезапустите сервер в Cursor IDE
