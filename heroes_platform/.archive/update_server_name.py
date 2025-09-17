#!/usr/bin/env python3
"""
Update MCP Server Name Script

Обновляет название MCP сервера с telegram-mcp на heroes-mcp для большей ясности.
"""

import json
from pathlib import Path


def update_server_name():
    """Обновить название MCP сервера"""
    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        print("❌ Cursor MCP config not found")
        return False

    try:
        # Читаем текущую конфигурацию
        with open(cursor_config_path) as f:
            config = json.load(f)

        # Проверяем, есть ли telegram-mcp
        if "mcpServers" in config and "telegram-mcp" in config["mcpServers"]:
            # Сохраняем конфигурацию telegram-mcp
            telegram_config = config["mcpServers"]["telegram-mcp"]

            # Удаляем старый ключ
            del config["mcpServers"]["telegram-mcp"]

            # Добавляем новый ключ heroes-mcp
            config["mcpServers"]["heroes-mcp"] = telegram_config

            print("✅ Updated server name from 'telegram-mcp' to 'heroes-mcp'")
        else:
            print("❌ telegram-mcp not found in Cursor config")
            return False

        # Сохраняем обновленную конфигурацию
        with open(cursor_config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ MCP server name updated successfully")
        return True

    except Exception as e:
        print(f"❌ Error updating server name: {e}")
        return False

def main():
    print("🔄 Updating MCP Server Name...")
    print("=" * 40)

    success = update_server_name()

    if success:
        print("\n🎉 Server name updated!")
        print("Now the server is called 'heroes-mcp' instead of 'telegram-mcp'")
        print("This better reflects that it's a comprehensive MCP server with multiple tools")
    else:
        print("\n❌ Failed to update server name")

if __name__ == "__main__":
    main()
