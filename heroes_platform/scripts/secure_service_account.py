#!/usr/bin/env python3
"""
Скрипт для безопасного сохранения Service Account JSON в Keychain
JTBD: Как разработчик, я хочу сохранить Service Account JSON в Keychain
и удалить файл из папки для безопасности.
"""

import json
import subprocess
from pathlib import Path


def save_to_keychain(json_data):
    """Сохранить JSON в Keychain"""
    try:
        json_string = json.dumps(json_data, indent=2)
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-s",
                "google-service-account-json",
                "-a",
                "rick@service",
                "-w",
                json_string,
            ],
            check=True,
            capture_output=True,
        )
        print("✅ Service Account JSON сохранен в Keychain")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сохранения в Keychain: {e}")
        return False


def delete_file(file_path):
    """Удалить файл"""
    try:
        Path(file_path).unlink()
        print(f"✅ Файл удален: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка удаления файла: {e}")
        return False


def update_mcp_config():
    """Обновить конфигурацию MCP для использования Keychain"""
    mcp_config_path = Path(".cursor/mcp.json")

    if not mcp_config_path.exists():
        print("❌ Файл .cursor/mcp.json не найден")
        return False

    try:
        with open(mcp_config_path) as f:
            config = json.load(f)

        # Обновить конфигурацию Google Sheets
        if "mcpServers" in config and "google-sheets" in config["mcpServers"]:
            config["mcpServers"]["google-sheets"]["env"][
                "GOOGLE_SERVICE_ACCOUNT_KEY"
            ] = "keychain:google-service-account-json"

        # Обновить конфигурацию Google Drive
        if "mcpServers" in config and "google-drive" in config["mcpServers"]:
            config["mcpServers"]["google-drive"]["env"][
                "GOOGLE_SERVICE_ACCOUNT_KEY"
            ] = "keychain:google-service-account-json"

        with open(mcp_config_path, "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Конфигурация MCP обновлена для использования Keychain")
        return True

    except Exception as e:
        print(f"❌ Ошибка обновления конфигурации MCP: {e}")
        return False


def main():
    print("🔐 Безопасное сохранение Service Account JSON")
    print("=" * 50)

    json_file_path = "heroes-platform/config/rick-google-service-account.json"

    # Читаем JSON
    with open(json_file_path) as f:
        json_data = json.load(f)

    # Сохраняем в Keychain
    if save_to_keychain(json_data):
        # Удаляем файл
        delete_file(json_file_path)
        print("🎉 Service Account JSON защищен!")


if __name__ == "__main__":
    main()
