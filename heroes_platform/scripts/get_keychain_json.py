#!/usr/bin/env python3
"""
Скрипт для извлечения Service Account JSON из Keychain
JTBD: Как разработчик, я хочу извлечь JSON из Keychain
для использования в MCP серверах.
"""

import json
import subprocess
import tempfile


def get_json_from_keychain():
    """Получить JSON из Keychain"""
    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                "google-service-account-json",
                "-a",
                "rick@service",
                "-w",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Декодируем hex данные
        hex_data = result.stdout.strip()
        json_string = subprocess.run(
            ["xxd", "-r", "-p"],
            input=hex_data,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        json_data = json.loads(json_string)
        return json_data

    except subprocess.CalledProcessError:
        print("❌ JSON не найден в Keychain")
        return None
    except json.JSONDecodeError:
        print("❌ Ошибка парсинга JSON из Keychain")
        return None


def create_temp_json_file(json_data):
    """Создать временный JSON файл"""
    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", prefix="service-account-", delete=False
        )

        json.dump(json_data, temp_file, indent=2)
        temp_file.close()

        print(f"✅ Временный файл создан: {temp_file.name}")
        return temp_file.name

    except Exception as e:
        print(f"❌ Ошибка создания временного файла: {e}")
        return None


def main():
    print("🔑 Извлечение Service Account JSON из Keychain")
    print("=" * 50)

    json_data = get_json_from_keychain()
    if not json_data:
        return

    print("✅ JSON получен из Keychain")
    print(f"📧 Client Email: {json_data.get('client_email', 'N/A')}")
    print(f"🔑 Key ID: {json_data.get('private_key_id', 'N/A')}")

    temp_file = create_temp_json_file(json_data)
    if temp_file:
        print()
        print("📋 Использование:")
        print(f"export GOOGLE_SERVICE_ACCOUNT_KEY='{temp_file}'")
        print("mcp-google-sheets-server")


if __name__ == "__main__":
    main()
