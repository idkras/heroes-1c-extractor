#!/usr/bin/env python3
"""
Скрипт для получения Yandex Direct OAuth 2.0 tokens
JTBD: Как разработчик, я хочу получить Client ID, Client Secret и Access Token для Yandex Direct API,
чтобы MCP сервер мог читать данные из рекламных кампаний.
"""

import subprocess
import sys
import webbrowser
from urllib.parse import urlencode

import requests

# OAuth 2.0 configuration для Яндекс.Директ
# Эти данные нужно получить в https://oauth.yandex.ru/client/new
CLIENT_ID = "YOUR_YANDEX_CLIENT_ID"  # Замените на ваш Client ID
REDIRECT_URI = "http://localhost:8080"
SCOPE = "direct:read"  # Права на чтение данных Яндекс.Директ


def get_client_credentials():
    """Получить Client ID и Client Secret от пользователя"""
    print("KEY: Получение Client Credentials для Яндекс.Директ", file=sys.stderr)
    print("1. Зайдите в [Yandex OAuth](https://oauth.yandex.ru/client/new)")
    print("2. Создайте новое приложение или используйте существующее")
    print("3. В настройках приложения найдите:")
    print("   - Client ID")
    print("   - Client Secret")
    print("4. Убедитесь что в настройках указан redirect URI: http://localhost:8080")
    print("5. В правах доступа включите: direct:read")
    print()

    client_id = input("Введите Client ID: ").strip()
    if not client_id:
        print("ERROR: Client ID не может быть пустым")
        return None, None

    client_secret = input("Введите Client Secret: ").strip()
    if not client_secret:
        print("ERROR: Client Secret не может быть пустым")
        return None, None

    return client_id, client_secret


def get_authorization_code(client_id):
    """Получить authorization code через браузер"""
    print("🌐 Получение authorization code")

    # Step 1: Get authorization URL
    auth_url = "https://oauth.yandex.ru/authorize"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }

    auth_url_with_params = f"{auth_url}?{urlencode(params)}"
    print("Открываю браузер для авторизации...")
    webbrowser.open(auth_url_with_params)

    print()
    print("После авторизации в браузере:")
    print("1. Скопируйте URL из адресной строки")
    print("2. Найдите параметр 'code=' в URL")
    print("3. Скопируйте значение после 'code='")
    print()

    auth_code = input("Введите authorization code: ").strip()
    if not auth_code:
        print("ERROR: Authorization code не может быть пустым")
        return None

    return auth_code


def exchange_code_for_tokens(client_id, client_secret, auth_code):
    """Обменять authorization code на tokens"""
    print("🔄 Обмен authorization code на tokens")

    token_url = "https://oauth.yandex.ru/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        tokens = response.json()

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        if not access_token:
            print("ERROR: Access token не получен")
            return None

        if not refresh_token:
            print(
                "WARNING: Refresh token не получен. Возможно, нужно переавторизоваться."
            )
            return None

        print("SUCCESS: Tokens получены успешно!")
        return tokens

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Ошибка при получении tokens: {e}")
        return None


def save_to_keychain(client_id, client_secret, access_token, refresh_token):
    """Сохранить данные в macOS Keychain"""
    try:
        # Сохраняем Client ID
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "heroes-mcp",
                "-s",
                "yandex_direct_client_id",
                "-w",
                client_id,
            ],
            check=True,
        )
        print("SUCCESS: Client ID сохранен в Keychain")

        # Сохраняем Client Secret
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "heroes-mcp",
                "-s",
                "yandex_direct_client_secret",
                "-w",
                client_secret,
            ],
            check=True,
        )
        print("SUCCESS: Client Secret сохранен в Keychain")

        # Сохраняем Access Token
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "heroes-mcp",
                "-s",
                "yandex_direct_access_token",
                "-w",
                access_token,
            ],
            check=True,
        )
        print("SUCCESS: Access Token сохранен в Keychain")

        # Сохраняем Refresh Token
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                "heroes-mcp",
                "-s",
                "yandex_direct_refresh_token",
                "-w",
                refresh_token,
            ],
            check=True,
        )
        print("SUCCESS: Refresh Token сохранен в Keychain")

        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Ошибка сохранения в Keychain: {e}")
        return False


def main():
    """Главная функция"""
    print("STARTING: Yandex Direct OAuth 2.0 Token Setup")
    print("=" * 50)

    # Получаем Client Credentials
    client_id, client_secret = get_client_credentials()
    if not client_id or not client_secret:
        print("ERROR: Не удалось получить Client Credentials")
        return

    # Получаем Authorization Code
    auth_code = get_authorization_code(client_id)
    if not auth_code:
        print("ERROR: Не удалось получить Authorization Code")
        return

    # Обмениваем на Tokens
    tokens = exchange_code_for_tokens(client_id, client_secret, auth_code)
    if not tokens:
        print("ERROR: Не удалось получить Tokens")
        return

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    # Сохраняем в Keychain
    if save_to_keychain(client_id, client_secret, access_token, refresh_token):
        print("\n🎉 Настройка завершена успешно!")
        print("Теперь MCP сервер может использовать Yandex Direct API")
        print("\nДоступные команды:")
        print("- yandex_direct_get_campaigns() - получить список кампаний")
        print("- yandex_direct_get_data(date_from, date_to) - получить данные кампаний")
    else:
        print("ERROR: Ошибка сохранения в Keychain")


if __name__ == "__main__":
    main()
