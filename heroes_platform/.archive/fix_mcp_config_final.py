#!/usr/bin/env python3
"""
Final MCP Configuration Fix Script

Исправляет MCP конфигурацию для использования обновленного mcp_server.py
вместо старого telegram-mcp проекта.
"""

import json
import subprocess
from pathlib import Path


def get_venv_python_path():
    """Получить путь к Python из виртуального окружения"""
    project_root = Path(__file__).parent
    venv_python = project_root / ".venv" / "bin" / "python3"

    if venv_python.exists():
        return str(venv_python)
    else:
        print("❌ Virtual environment Python not found")
        return None

def fix_cursor_config():
    """Исправить конфигурацию Cursor для использования обновленного mcp_server.py"""
    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        print("❌ Cursor MCP config not found")
        return False

    try:
        # Читаем текущую конфигурацию
        with open(cursor_config_path) as f:
            config = json.load(f)

        # Получаем путь к Python из venv
        venv_python = get_venv_python_path()
        if not venv_python:
            return False

        # Путь к обновленному mcp_server.py
        mcp_server_path = Path(__file__).parent / "platform" / "mcp_server" / "src" / "mcp_server.py"

        if not mcp_server_path.exists():
            print(f"❌ MCP server not found at: {mcp_server_path}")
            return False

        # Обновляем конфигурацию telegram-mcp
        if "mcpServers" in config and "telegram-mcp" in config["mcpServers"]:
            config["mcpServers"]["telegram-mcp"]["command"] = venv_python
            config["mcpServers"]["telegram-mcp"]["args"] = [str(mcp_server_path)]
            print(f"✅ Updated Cursor config to use: {venv_python}")
            print(f"✅ Updated args to: {mcp_server_path}")
        else:
            print("❌ telegram-mcp not found in Cursor config")
            return False

        # Сохраняем обновленную конфигурацию
        with open(cursor_config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ Cursor MCP configuration fixed successfully")
        return True

    except Exception as e:
        print(f"❌ Error fixing Cursor config: {e}")
        return False

def test_mcp_server():
    """Протестировать обновленный MCP сервер"""
    print("🧪 Testing updated MCP server...")

    try:
        mcp_server_path = Path(__file__).parent / "platform" / "mcp_server" / "src" / "mcp_server.py"

        # Тестируем сервер
        result = subprocess.run(
            f"source .venv/bin/activate && python {mcp_server_path} --test",
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )

        if result.returncode == 0:
            print("✅ MCP server test passed")
            print("📋 Available tools:")
            print(result.stdout)
            return True
        else:
            print(f"❌ MCP server test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def main():
    print("🔧 Final MCP Configuration Fix...")
    print("=" * 50)

    # Проверяем виртуальное окружение
    venv_python = get_venv_python_path()
    if venv_python:
        print(f"✅ Virtual environment Python: {venv_python}")
    else:
        print("❌ Virtual environment not found")
        return

    # Исправляем конфигурацию
    cursor_fixed = fix_cursor_config()

    # Тестируем MCP сервер
    server_works = test_mcp_server()

    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Cursor config: {'✅ Fixed' if cursor_fixed else '❌ Failed'}")
    print(f"MCP server: {'✅ Working' if server_works else '❌ Failed'}")

    if cursor_fixed and server_works:
        print("\n🔄 Next steps:")
        print("1. Restart Cursor")
        print("2. Check MCP Tools settings")
        print("3. Test telegram-mcp commands")
        print("\n🎉 Configuration updated successfully!")
        print("Now telegram-mcp will use the integrated mcp_server.py instead of the old project")

if __name__ == "__main__":
    main()
