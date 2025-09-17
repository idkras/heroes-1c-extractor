# Heroes MCP Server Setup

## Обзор

Heroes MCP Server предоставляет инструменты для работы со стандартами проекта и AI workflow через Cursor IDE.

## Доступные инструменты

1. **server_info** - Информация о сервере
2. **standards_management** - Управление стандартами проекта
3. **heroes_gpt_workflow** - Анализ лендингов и контента
4. **performance_monitor** - Мониторинг производительности

## Настройка в Cursor

### 1. Конфигурация MCP

Файл `.cursor/mcp.json` уже настроен:

```json
{
  "mcpServers": {
    "heroes-mcp": {
      "command": "python3",
      "args": ["platform/mcp_server/run_mcp_server.py"],
      "env": {
        "PYTHONPATH": "platform/mcp_server/src"
      }
    }
  }
}
```

### 2. Зависимости

Убедитесь, что установлены необходимые пакеты:

```bash
pip install mcp fastmcp
```

### 3. Тестирование

Для проверки работы сервера:

```bash
cd /path/to/heroes-template
python3 platform/mcp_server/run_mcp_server.py --test
```

### 4. Перезапуск Cursor

После изменения настроек MCP перезапустите Cursor для применения изменений.

## Структура файлов

```
platform/mcp_server/
├── src/
│   └── mcp_server.py          # Основной MCP сервер
├── run_mcp_server.py          # Скрипт запуска с настройкой окружения
├── mcp_config.json            # Конфигурация инструментов
└── MCP_SETUP.md              # Эта документация
```

## Устранение неполадок

### Проблема: "MCP server not found"
- Проверьте, что файл `.cursor/mcp.json` существует
- Убедитесь, что пути в конфигурации корректны
- Перезапустите Cursor

### Проблема: "Import error"
- Проверьте установку зависимостей: `pip install mcp fastmcp`
- Убедитесь, что PYTHONPATH настроен правильно

### Проблема: "Multiple MCP configurations"
- Удалите дублирующиеся файлы mcp.json
- Оставьте только один файл в `.cursor/mcp.json`

## Использование инструментов

### Standards Management
```python
# Список стандартов
standards_management(command="list")

# Поиск стандартов
standards_management(command="search", query="task")

# Получение содержимого
standards_management(command="get", path="0. core standards/0.0 task master.md")
```

### Heroes GPT Workflow
```python
# Анализ URL
heroes_gpt_workflow(action="analyze", url="https://example.com")

# Генерация контента
heroes_gpt_workflow(action="generate", prompt="Создать лендинг для SaaS")
```

### Performance Monitor
```python
# Статус системы
performance_monitor(metric="status")

# Использование памяти
performance_monitor(metric="memory")

# Использование CPU
performance_monitor(metric="cpu")
```
