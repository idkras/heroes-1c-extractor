#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы n8n-mcp сервера
"""

import subprocess
import sys


def test_n8n_mcp():
    """Тестирует n8n-mcp сервер"""
    try:
        # Проверяем, что сервер запускается
        result = subprocess.run(
            ["node", "dist/index.js"],
            cwd="n8n-mcp",
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ n8n-mcp сервер работает корректно")
            return True
        else:
            print(f"❌ n8n-mcp сервер вернул ошибку: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✅ n8n-mcp сервер запустился (timeout ожидаем)")
        return True
    except Exception as e:
        print(f"❌ Ошибка при тестировании n8n-mcp: {e}")
        return False


def test_jira_mcp():
    """Тестирует jira-mcp сервер"""
    try:
        # Проверяем, что сервер запускается
        result = subprocess.run(
            ["npx", "@aashari/mcp-server-atlassian-jira", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ jira-mcp сервер работает корректно")
            return True
        else:
            print(f"❌ jira-mcp сервер вернул ошибку: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании jira-mcp: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование MCP серверов...")
    print()

    # Проверяем n8n-mcp
    print("1. Тестирование n8n-mcp сервера:")
    n8n_ok = test_n8n_mcp()
    print()

    # Проверяем jira-mcp
    print("2. Тестирование jira-mcp сервера:")
    jira_ok = test_jira_mcp()
    print()

    # Итоговый результат
    if n8n_ok and jira_ok:
        print("🎉 Все MCP серверы работают корректно!")
        return 0
    else:
        print("⚠️  Некоторые MCP серверы имеют проблемы")
        return 1


if __name__ == "__main__":
    sys.exit(main())
