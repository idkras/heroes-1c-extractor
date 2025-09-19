#!/usr/bin/env python3
"""
Restore Telegram MCP Configuration Script

Восстанавливает telegram-mcp конфигурацию и исправляет название файла.
"""

import json
from pathlib import Path


def restore_telegram_mcp_config():
    """Восстановить telegram-mcp конфигурацию"""
    cursor_config_path = Path.home() / ".cursor" / "mcp.json"

    if not cursor_config_path.exists():
        print("❌ Cursor MCP config not found")
        return False

    try:
        # Читаем текущую конфигурацию
        with open(cursor_config_path) as f:
            config = json.load(f)

        # Получаем путь к Python из виртуального окружения telegram-mcp
        telegram_venv_python = (
            Path(__file__).parent / "telegram-mcp" / ".venv" / "bin" / "python3"
        )

        if not telegram_venv_python.exists():
            print("❌ Telegram MCP virtual environment not found")
            return False

        # Путь к файлу main_keychain.py
        main_keychain_path = Path(__file__).parent / "telegram-mcp" / "main_keychain.py"

        if not main_keychain_path.exists():
            print(f"❌ main_keychain.py not found at: {main_keychain_path}")
            return False

        # Добавляем telegram-mcp конфигурацию
        config["mcpServers"]["telegram-mcp"] = {
            "command": str(telegram_venv_python),
            "args": [str(main_keychain_path)],
        }

        print("✅ Added telegram-mcp config:")
        print(f"   Command: {telegram_venv_python}")
        print(f"   Args: {main_keychain_path}")

        # Сохраняем обновленную конфигурацию
        with open(cursor_config_path, "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Telegram MCP configuration restored successfully")
        return True

    except Exception as e:
        print(f"❌ Error restoring telegram-mcp config: {e}")
        return False


def rename_main_keychain_file():
    """Переименовать main_keychain.py в более понятное название"""
    old_path = Path(__file__).parent / "telegram-mcp" / "main_keychain.py"
    new_path = Path(__file__).parent / "telegram-mcp" / "telegram_mcp_server.py"

    if not old_path.exists():
        print(f"❌ File not found: {old_path}")
        return False

    try:
        # Переименовываем файл
        old_path.rename(new_path)
        print(f"✅ Renamed {old_path.name} to {new_path.name}")

        # Обновляем конфигурацию
        cursor_config_path = Path.home() / ".cursor" / "mcp.json"

        if cursor_config_path.exists():
            with open(cursor_config_path) as f:
                config = json.load(f)

            if "telegram-mcp" in config["mcpServers"]:
                config["mcpServers"]["telegram-mcp"]["args"] = [str(new_path)]

                with open(cursor_config_path, "w") as f:
                    json.dump(config, f, indent=2)

                print(f"✅ Updated MCP config to use {new_path.name}")

        return True

    except Exception as e:
        print(f"❌ Error renaming file: {e}")
        return False


def main():
    print("🔄 Restoring Telegram MCP Configuration...")
    print("=" * 50)

    # Восстанавливаем конфигурацию
    config_restored = restore_telegram_mcp_config()

    # Переименовываем файл
    file_renamed = rename_main_keychain_file()

    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Config restored: {'✅ Yes' if config_restored else '❌ No'}")
    print(f"File renamed: {'✅ Yes' if file_renamed else '❌ No'}")

    if config_restored and file_renamed:
        print("\n🎉 Success!")
        print("telegram-mcp configuration restored with better file naming")
        print(
            "File is now called 'telegram_mcp_server.py' instead of 'main_keychain.py'"
        )


if __name__ == "__main__":
    main()
