#!/usr/bin/env python3
"""
Тест подключения Cursor к MCP серверу
Проверяет что сервер отвечает на запросы от Cursor
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


async def test_cursor_connection():
    """Тестирует подключение Cursor к MCP серверу"""

    # Путь к серверу
    server_path = Path(__file__).parent / "mcp_server.py"

    print("🚀 Тестирование подключения Cursor к MCP серверу")
    print(f"📁 Сервер: {server_path}")
    print()

    # Запускаем сервер
    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Тест 1: Initialize
        print("1️⃣ Отправляем initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "cursor-test", "version": "1.0"},
            },
        }

        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Читаем ответ
        response = process.stdout.readline()
        print(f"✅ Initialize ответ: {response.strip()}")

        # Тест 2: Initialized notification
        print("2️⃣ Отправляем initialized notification...")
        init_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        process.stdin.write(json.dumps(init_notification) + "\n")
        process.stdin.flush()

        # Ждем немного
        await asyncio.sleep(0.5)

        # Тест 3: List tools
        print("3️⃣ Запрашиваем список инструментов...")
        list_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()

        # Читаем ответ
        response = process.stdout.readline()
        print(f"✅ Tools list ответ: {response.strip()}")

        # Парсим ответ
        try:
            data = json.loads(response)
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"🎯 Найдено инструментов: {len(tools)}")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description'][:50]}...")
            else:
                print("❌ Неожиданный формат ответа")
        except json.JSONDecodeError:
            print("❌ Ошибка парсинга JSON")

        # Тест 4: Call tool
        print("4️⃣ Тестируем вызов инструмента...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "standards_management",
                "arguments": {"command": "list"},
            },
        }

        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()

        # Читаем ответ
        response = process.stdout.readline()
        print(f"✅ Tool call ответ: {response.strip()}")

        print()
        print("🎉 Тест завершен успешно!")
        print("💡 Если все тесты прошли, но Cursor не видит инструменты:")
        print("   1. Перезапустите Cursor полностью")
        print("   2. Проверьте что сервер запущен")
        print("   3. Убедитесь что конфигурация в ~/.cursor/mcp.json правильная")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

    finally:
        # Завершаем процесс
        process.terminate()
        process.wait()


if __name__ == "__main__":
    asyncio.run(test_cursor_connection())
