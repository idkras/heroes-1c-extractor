# Heroes MCP Server

MCP сервер для работы со стандартами и инструментами, интегрированный с Cursor.

## 🚀 Быстрый запуск

### Правильная команда

```bash
cd "[standards .md]/platform/mcp_server/src"
python3 mcp_server.py
```

### Или используйте скрипт

```bash
cd "[standards .md]/platform/mcp_server/src"
./start_server.sh
```

### Важно

- **НЕ используйте** `nohup`, `&` или перенаправление stdout/stderr
- **stdio transport** использует stdin/stdout для JSON-RPC
- Сервер блокирует выполнение и ждет подключения от Cursor
- Логи автоматически идут в stderr

## 📋 Доступные инструменты

1. **standards_management** - управление стандартами
2. **heroes_gpt_workflow** - HeroesGPT анализ лендингов
3. **performance_monitor** - мониторинг производительности

## 🔧 Интеграция с Cursor

1. Запустите сервер командой выше
2. Перезапустите Cursor полностью
3. Проверьте в Command Palette (Cmd+Shift+P) -> "MCP"
4. Должен появиться "heroes-mcp" с 3 инструментами

## 🐛 Диагностика проблем

### Race condition в Cursor

Если Cursor показывает "No tools or prompts", это race condition:

- Cursor отправляет `tools/list` до завершения инициализации
- Сервер отклоняет запрос как "Failed to validate request"

### Решение

1. Перезапустите Cursor полностью
2. Убедитесь что сервер запущен и ждет подключения
3. Проверьте конфигурацию в `~/.cursor/mcp.json`

## 📚 Официальная документация

- **FastMCP**: `mcp.run(transport="stdio")` - синхронная функция
- **Transport**: stdio использует stdin/stdout для JSON-RPC
- **Логирование**: автоматически в stderr, не мешает протоколу
