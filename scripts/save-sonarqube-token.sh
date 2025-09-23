#!/bin/bash

# SonarQube Token Saver Script
# Сохраняет токен SonarQube в macOS Keychain через credentials_manager

set -e

echo "🔑 Сохранение токена SonarQube в Keychain"
echo "========================================"

# Проверка Python и credentials_manager
if ! python3 -c "import sys; sys.path.append('heroes_platform'); from shared.credentials_manager import credentials_manager" 2>/dev/null; then
    echo "❌ Не удалось импортировать credentials_manager"
    echo "Убедитесь, что вы находитесь в корневой директории проекта"
    exit 1
fi

# Запрос токена от пользователя
echo "📝 Введите токен SonarQube (начинается с sqa_):"
read -r SONAR_TOKEN

if [[ ! "$SONAR_TOKEN" =~ ^sqa_ ]]; then
    echo "❌ Токен должен начинаться с 'sqa_'"
    exit 1
fi

# Запрос URL
echo "🌐 Введите URL SonarQube (по умолчанию: http://localhost:9000):"
read -r SONAR_HOST_URL
SONAR_HOST_URL=${SONAR_HOST_URL:-"http://localhost:9000"}

# Запрос организации
echo "🏢 Введите организацию SonarQube (по умолчанию: heroes-platform):"
read -r SONAR_ORGANIZATION
SONAR_ORGANIZATION=${SONAR_ORGANIZATION:-"heroes-platform"}

# Сохранение через credentials_manager
echo "💾 Сохранение токенов в Keychain..."

python3 -c "
import sys
sys.path.append('heroes_platform')
from shared.credentials_manager import credentials_manager

# Сохранение токена
token_result = credentials_manager.store_credential('sonar_token', '$SONAR_TOKEN', 'keychain')
if token_result:
    print('✅ SonarQube Token сохранен в Keychain')
else:
    print('❌ Ошибка сохранения SonarQube Token')
    exit(1)

# Сохранение URL
url_result = credentials_manager.store_credential('sonar_host_url', '$SONAR_HOST_URL', 'keychain')
if url_result:
    print('✅ SonarQube Host URL сохранен в Keychain')
else:
    print('❌ Ошибка сохранения SonarQube Host URL')
    exit(1)

# Сохранение организации
org_result = credentials_manager.store_credential('sonar_organization', '$SONAR_ORGANIZATION', 'keychain')
if org_result:
    print('✅ SonarQube Organization сохранена в Keychain')
else:
    print('❌ Ошибка сохранения SonarQube Organization')
    exit(1)

print('🎯 Все токены SonarQube успешно сохранены в Keychain!')
"

# Тестирование подключения
echo "🧪 Тестирование подключения к SonarQube..."
if curl -s -f -H "Authorization: Bearer $SONAR_TOKEN" "$SONAR_HOST_URL/api/system/status" > /dev/null; then
    echo "✅ Подключение к SonarQube успешно"
else
    echo "❌ Ошибка подключения к SonarQube"
    echo "Проверьте токен и URL"
fi

echo ""
echo "🎯 Настройка завершена!"
echo ""
echo "📋 Сохраненные токены:"
echo "  - sonar_token: $SONAR_TOKEN"
echo "  - sonar_host_url: $SONAR_HOST_URL"
echo "  - sonar_organization: $SONAR_ORGANIZATION"
echo ""
echo "🚀 Теперь можно использовать:"
echo "  make sonar-scan"
echo "  make sonar-local"
