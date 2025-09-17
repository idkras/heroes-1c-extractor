# 🔍 План диагностики MCP сервера

## 📋 Анализ текущего состояния

### ✅ Что работает

- Сервер запускается без ошибок
- FastMCP инициализируется корректно
- 4 инструмента зарегистрированы
- Конфигурация Cursor настроена

### ❌ Проблемы

- Cursor не видит tools
- Не проходит этапы initialize → notifications/initialized → tools/list
- Возможные race conditions

## 🎯 План тестирования

### 1. **Базовые тесты сервера**

#### 1.1 Тест запуска сервера

```bash
cd "[standards .md]/platform/mcp_server/src"
python3 mcp_server.py --test
```

**Ожидаемый результат:** "Registered tools: server_info, standards_management, heroes_gpt_workflow, performance_monitor"

#### 1.2 Тест зависимостей

```bash
source .venv/bin/activate
pip show mcp
python3 -c "from mcp.server import FastMCP; print('FastMCP доступен')"
```

**Ожидаемый результат:** Версия mcp и подтверждение импорта

### 2. **Тесты JSON-RPC протокола**

#### 2.1 Тест правильной последовательности

```bash
# Создаем тестовый скрипт
cat > test_protocol.sh << 'EOF'
#!/bin/bash
cd "[standards .md]/platform/mcp_server/src"

# Запускаем сервер в фоне
python3 mcp_server.py &
SERVER_PID=$!

# Ждем запуска
sleep 2

# Тест 1: Initialize
echo "=== Тест 1: Initialize ==="
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | python3 mcp_server.py

# Тест 2: Initialized notification
echo "=== Тест 2: Initialized notification ==="
echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}' | python3 mcp_server.py

# Тест 3: Tools list
echo "=== Тест 3: Tools list ==="
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | python3 mcp_server.py

# Очистка
kill $SERVER_PID
EOF

chmod +x test_protocol.sh
./test_protocol.sh
```

#### 2.2 Тест race condition (проблема Cursor)

```bash
# Симуляция race condition - отправляем tools/list сразу после initialize
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 0.1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | python3 mcp_server.py
```

### 3. **Тесты интеграции с Cursor**

#### 3.1 Проверка конфигурации

```bash
# Проверяем конфигурацию
python3 -m json.tool ~/.cursor/mcp.json

# Проверяем пути
ls -la "/Users/ilyakrasinsky/workspace/vscode.projects/[cursor.template project]/[standards .md]/platform/mcp_server/src/mcp_server.py"
ls -la "/Users/ilyakrasinsky/workspace/vscode.projects/[cursor.template project]/.venv/bin/python3"
```

#### 3.2 Тест запуска через Cursor конфигурацию

```bash
# Запускаем сервер точно как Cursor
/Users/ilyakrasinsky/workspace/vscode.projects/[cursor.template\ project]/.venv/bin/python3 -u /Users/ilyakrasinsky/workspace/vscode.projects/[cursor.template\ project]/[standards\ .md]/platform/mcp_server/src/mcp_server.py
```

### 4. **Тесты инструментов**

#### 4.1 Тест server_info

```bash
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "server_info", "arguments": {}}}' | python3 mcp_server.py
```

#### 4.2 Тест standards_management

```bash
echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "standards_management", "arguments": {"command": "list"}}}' | python3 mcp_server.py
```

#### 4.3 Тест performance_monitor

```bash
echo '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "performance_monitor", "arguments": {"metric": "status"}}}' | python3 mcp_server.py
```

## 🔧 Возможные решения проблем

### Проблема 1: Race condition в Cursor

**Симптомы:** Cursor отправляет `tools/list` до завершения инициализации
**Решение:** Добавить tolerant_handle в сервер для ожидания инициализации

### Проблема 2: Неправильные пути в конфигурации

**Симптомы:** Сервер не запускается через Cursor
**Решение:** Проверить и исправить пути в `~/.cursor/mcp.json`

### Проблема 3: Проблемы с транспортом stdio

**Симптомы:** Нет связи между Cursor и сервером
**Решение:** Убедиться что сервер использует `transport="stdio"`

### Проблема 4: Проблемы с виртуальным окружением

**Симптомы:** Импорт ошибки или отсутствующие зависимости
**Решение:** Активировать правильное виртуальное окружение

## 📊 Результаты тестов

### ✅ Успешный тест протокола (ПОЛНОСТЬЮ ИСПРАВЛЕНО)

**Статус:** ВСЕ ТЕСТЫ ПРОХОДЯТ УСПЕШНО ✅

```
=== Тест 1: Initialize ===
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"heroes-mcp","version":"1.12.4"}}}

=== Тест 2: Initialized notification ===
(без ответа - это notification)

=== Тест 3: Tools list ===
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"server_info","description":"Get information about the current server.","inputSchema":{"properties":{},"title":"server_infoArguments","type":"object"},"outputSchema":{"properties":{"result":{"title":"Result","type":"string"}},"required":["result"],"title":"server_infoOutput","type":"object"}},{"name":"standards_management",...}]}}

=== Тест 4: Tool call ===
{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Heroes MCP Server v1.0.0 - Status: running, Tools: 4"}],"structuredContent":{"result":"Heroes MCP Server v1.0.0 - Status: running, Tools: 4"},"isError":false}}
```

**Проверено:**

- ✅ Сервер запускается без ошибок
- ✅ Initialize возвращает корректный ответ
- ✅ Tools/list возвращает 4 инструмента с правильными схемами
- ✅ Tools/call работает корректно
- ✅ Конфигурация Cursor корректна
- ✅ Все пути существуют и доступны

### ❌ Проблемы

- "Failed to validate request: Received request before initialization was complete"
- "Invalid request parameters"
- Пустые ответы или ошибки JSON

## 🚀 Следующие шаги

1. **Выполнить все тесты** по порядку
2. **Зафиксировать результаты** каждого теста
3. **Определить корневую причину** проблемы
4. **Применить соответствующее решение**
5. **Перезапустить Cursor** и проверить интеграцию
6. **Документировать решение** для будущих случаев

## 📝 Команды для быстрой диагностики

```bash
# Быстрая проверка
cd "[standards .md]/platform/mcp_server/src"
python3 mcp_server.py --test

# Проверка протокола
(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}'; sleep 1; echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'; sleep 1; echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}') | python3 mcp_server.py

# Проверка конфигурации
python3 -m json.tool ~/.cursor/mcp.json
```
