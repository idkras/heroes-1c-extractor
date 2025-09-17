# Команды для тестирования MCP сервера

## ✅ ПРОБЛЕМА ДИАГНОСТИРОВАНА И РЕШЕНА

**Корневая причина:** Race condition в Cursor - отправляет `tools/list` до завершения инициализации.

### Доказательство race condition

```bash
# ❌ Неправильная последовательность (как делает Cursor)
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 0.1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python3 mcp_server.py

# Результат: "Failed to validate request: Received request before initialization was complete"
```

```bash
# ✅ Правильная последовательность
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 1; echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'; sleep 1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python3 mcp_server.py

# Результат: Возвращает 3 инструмента успешно
```

## Решения проблемы

### 1. **Надежное решение** - буфер в сервере

Добавить tolerant_handle для ожидания инициализации (реализовано в коде)

### 2. **Быстрое решение** - обновить Cursor

Перезапустить Cursor полностью после изменения конфигурации

### 3. **Клиентское решение** - правильная конфигурация

Убедиться что пути в `~/.cursor/mcp.json` абсолютные и в кавычках

## Команды для тестирования

### 1. Тест race condition (демонстрация проблемы)

```bash
cd "[standards .md]/platform/mcp_server/src"
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 0.1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python3 mcp_server.py
```

### 2. Тест правильной последовательности

```bash
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 1; echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'; sleep 1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python3 mcp_server.py
```

### 3. Тест вызова инструмента

```bash
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 1; echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'; sleep 1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "standards_management", "arguments": {"command": "get_standards"}}}') | python3 mcp_server.py
```

### 4. Проверка конфигурации Cursor

```bash
python3 -m json.tool ~/.cursor/mcp.json
```

## Ожидаемые результаты

### ❌ При race condition

- "Failed to validate request: Received request before initialization was complete"
- "Invalid request parameters"
- Cursor показывает "No tools or prompts"

### ✅ При правильной последовательности

- Initialize возвращает успешный ответ с serverInfo
- List tools возвращает 3 инструмента:
  - `standards_management`
  - `heroes_gpt_workflow`
  - `performance_monitor`
- Call tool возвращает корректный результат с данными

## Для интеграции с Cursor

1. **Перезапустить Cursor полностью** (закрыть и открыть заново)
2. Проверить в Command Palette (Cmd+Shift+P) -> "MCP" -> должен появиться "heroes-mcp"
3. Протестировать инструменты через AI

## Проблема решена

Сервер работает корректно. Race condition в Cursor решается перезапуском или обновлением Cursor.
