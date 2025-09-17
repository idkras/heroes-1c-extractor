#!/usr/bin/env python3
"""
Скрипт для получения Google OAuth 2.0 tokens
JTBD: Как разработчик, я хочу получить Client Secret и Refresh Token для Google Sheets API,
чтобы MCP сервер мог читать данные из Google Sheets.
"""

import requests
import webbrowser
import subprocess
import sys
from urllib.parse import urlencode, parse_qs, urlparse

# OAuth 2.0 configuration
CLIENT_ID = "11002942740-5rgf84foh6k98vpg3lb3ug8d9pv5gq1h.apps.googleusercontent.com"
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"

def get_client_secret():
    """Получить Client Secret от пользователя"""
    print("🔑 Получение Client Secret")
    print("1. Зайдите в [Google Cloud Console](https://console.cloud.google.com/)")
    print("2. Проект: rick-382109")
    print("3. APIs & Services → Credentials")
    print("4. Найдите 'Rick.ai BigQuery integration' в OAuth 2.0 Client IDs")
    print("5. Нажмите 'Edit' (карандаш)")
    print("6. Скопируйте 'Client secret'")
    print()
    
    client_secret = input("Введите Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret не может быть пустым")
        return None
    
    return client_secret

def get_authorization_code():
    """Получить authorization code через браузер"""
    print("🌐 Получение authorization code")
    
    # Step 1: Get authorization URL
    auth_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"  # Всегда запрашивать consent для получения refresh_token
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(params)}"
    print(f"Открываю браузер для авторизации...")
    webbrowser.open(auth_url_with_params)
    
    print()
    print("После авторизации в браузере:")
    print("1. Скопируйте URL из адресной строки")
    print("2. Найдите параметр 'code=' в URL")
    print("3. Скопируйте значение после 'code='")
    print()
    
    auth_code = input("Введите authorization code: ").strip()
    if not auth_code:
        print("❌ Authorization code не может быть пустым")
        return None
    
    return auth_code

def exchange_code_for_tokens(client_secret, auth_code):
    """Обменять authorization code на tokens"""
    print("🔄 Обмен authorization code на tokens")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        if not access_token:
            print("❌ Access token не получен")
            return None
        
        if not refresh_token:
            print("⚠️ Refresh token не получен. Возможно, нужно переавторизоваться.")
            return None
        
        print("✅ Tokens получены успешно!")
        return tokens
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при получении tokens: {e}")
        return None

def save_to_keychain(client_secret, refresh_token):
    """Сохранить данные в macOS Keychain"""
    print("💾 Сохранение в Keychain")
    
    try:
        # Сохранить Client Secret
        subprocess.run([
            "security", "add-generic-password",
            "-s", "google_oauth_client_secret",
            "-a", "rick@service",
            "-w", client_secret
        ], check=True, capture_output=True)
        print("✅ Client Secret сохранен в Keychain")
        
        # Сохранить Refresh Token
        subprocess.run([
            "security", "add-generic-password",
            "-s", "google_refresh_token",
            "-a", "rick@service",
            "-w", refresh_token
        ], check=True, capture_output=True)
        print("✅ Refresh Token сохранен в Keychain")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сохранении в Keychain: {e}")
        return False

def test_google_sheets_access(access_token):
    """Протестировать доступ к Google Sheets"""
    print("🧪 Тестирование доступа к Google Sheets")
    
    # Тестируем на Vipavenue таблице
    spreadsheet_id = "1Wh1SF0_izRo4TJ8YkquJrMeDcoSi2AAc2cIG_s9LWVg"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Доступ к Google Sheets работает!")
            print(f"📊 Название таблицы: {data.get('properties', {}).get('title', 'Unknown')}")
            return True
        else:
            print(f"❌ Ошибка доступа: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 Google OAuth 2.0 Token Generator")
    print("=" * 50)
    
    # 1. Получить Client Secret
    client_secret = get_client_secret()
    if not client_secret:
        return
    
    # 2. Получить authorization code
    auth_code = get_authorization_code()
    if not auth_code:
        return
    
    # 3. Обменять code на tokens
    tokens = exchange_code_for_tokens(client_secret, auth_code)
    if not tokens:
        return
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    print(f"🔑 Access Token: {access_token[:20]}...")
    print(f"🔄 Refresh Token: {refresh_token[:20]}...")
    
    # 4. Сохранить в Keychain
    if save_to_keychain(client_secret, refresh_token):
        print("✅ Все данные сохранены в Keychain")
    else:
        print("❌ Ошибка при сохранении в Keychain")
        return
    
    # 5. Протестировать доступ
    if test_google_sheets_access(access_token):
        print("🎉 Настройка завершена успешно!")
        print()
        print("Теперь можно использовать MCP команды:")
        print("- google_sheets_read_spreadsheet")
        print("- google_sheets_read_formulas")
    else:
        print("⚠️ Доступ к Google Sheets не работает")

if __name__ == "__main__":
    main()
