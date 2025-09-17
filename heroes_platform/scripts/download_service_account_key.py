#!/usr/bin/env python3
"""
Скрипт для скачивания Service Account ключа
JTBD: Как разработчик, я хочу скачать полный JSON ключ Service Account,
чтобы настроить аутентификацию для Google Sheets MCP.
"""

import json
import subprocess
import sys
from pathlib import Path

def get_key_from_keychain():
    """Получить ключ из Keychain"""
    try:
        result = subprocess.run([
            "security", "find-generic-password",
            "-s", "google-service-account-key-id",
            "-a", "rick@service",
            "-w"
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Ключ не найден в Keychain")
        return None

def create_service_account_json():
    """Создать JSON файл Service Account"""
    key_id = get_key_from_keychain()
    if not key_id:
        return False
    
    # Данные Service Account
    service_account_data = {
        "type": "service_account",
        "project_id": "rick-382109",
        "private_key_id": key_id,
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "n8n-heroes-rickai-service-acco@rick-382109.iam.gserviceaccount.com",
        "client_id": "11002942740-5rgf84foh6k98vpg3lb3ug8d9pv5gq1h.apps.googleusercontent.com",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/n8n-heroes-rickai-service-acco%40rick-382109.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    # Путь к файлу
    config_dir = Path("heroes-platform/config")
    config_dir.mkdir(exist_ok=True)
    json_file = config_dir / "rick-google-service-account.json"
    
    # Сохранить JSON
    with open(json_file, 'w') as f:
        json.dump(service_account_data, f, indent=2)
    
    print(f"✅ JSON файл создан: {json_file}")
    print(f"🔑 Key ID: {key_id}")
    print()
    print("⚠️ ВАЖНО: Нужно заменить 'YOUR_PRIVATE_KEY_HERE' на реальный private key!")
    print("1. Зайдите в Google Cloud Console")
    print("2. IAM & Admin → Service Accounts")
    print("3. Найдите 'n8n-heroes-rickai-service-acco@rick-382109.iam.gserviceaccount.com'")
    print("4. Keys → Add Key → Create new key → JSON")
    print("5. Скачайте JSON файл")
    print("6. Скопируйте private_key из скачанного файла")
    
    return True

def main():
    """Главная функция"""
    print("🔑 Service Account Key Downloader")
    print("=" * 40)
    
    if create_service_account_json():
        print()
        print("📋 Следующие шаги:")
        print("1. Скачайте полный JSON ключ из Google Cloud Console")
        print("2. Замените private_key в файле")
        print("3. Протестируйте Google Sheets MCP")
    else:
        print("❌ Ошибка при создании JSON файла")

if __name__ == "__main__":
    main()
