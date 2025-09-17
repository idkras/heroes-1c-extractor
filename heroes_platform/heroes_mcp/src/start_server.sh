#!/bin/bash

# Heroes MCP Server Launcher
# Запускает MCP сервер для интеграции с Cursor

echo "🚀 Запуск Heroes MCP Server..."
echo "📁 Директория: $(pwd)"
echo "🐍 Python: $(which python3)"
echo ""

# Проверяем что файл существует
if [ ! -f "mcp_server.py" ]; then
    echo "❌ Ошибка: mcp_server.py не найден!"
    exit 1
fi

# Запускаем сервер
echo "✅ Запуск сервера..."
python3 mcp_server.py

echo ""
echo "👋 Сервер завершен"
