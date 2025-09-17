#!/bin/bash

# Heroes MCP Server Launcher
# Запускает MCP сервер для интеграции с Cursor

echo "🚀 Запуск Heroes MCP Server..."
echo "📁 Директория: $(pwd)"
echo "🐍 Python: $(which python3)"
echo ""

# Проверяем что файл существует
if [ ! -f "src/heroes_mcp_server.py" ]; then
    echo "❌ Ошибка: src/heroes_mcp_server.py не найден!"
    exit 1
fi

# Запускаем сервер
echo "✅ Запуск сервера..."
python3 src/heroes_mcp_server.py

echo ""
echo "👋 Сервер завершен"
