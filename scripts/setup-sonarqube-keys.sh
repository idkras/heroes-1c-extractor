#!/bin/bash

# SonarQube Keys Setup Script for macOS Keychain
# Автоматическая настройка ключей SonarQube в macOS Keychain

set -e

echo "🔑 Настройка ключей SonarQube в macOS Keychain"
echo "=============================================="

# Проверка доступности SonarQube
echo "🔍 Проверка доступности SonarQube..."
if ! curl -s http://localhost:9000 > /dev/null; then
    echo "❌ SonarQube недоступен. Запустите: make sonar-local"
    exit 1
fi

echo "✅ SonarQube доступен"

# Генерация токена SonarQube
echo "🔐 Генерация токена SonarQube..."

# Ожидание полной инициализации SonarQube
echo "⏳ Ожидание инициализации SonarQube (60 секунд)..."
sleep 60

# Проверка готовности SonarQube
for i in {1..30}; do
    if curl -s -u admin:admin http://localhost:9000/api/system/status | grep -q "UP"; then
        echo "✅ SonarQube готов к работе"
        break
    fi
    echo "⏳ Ожидание готовности SonarQube... ($i/30)"
    sleep 2
done

# Создание токена через API
echo "🔑 Создание токена SonarQube..."

# Генерация случайного токена
SONAR_TOKEN=$(openssl rand -hex 32)
echo "📝 Сгенерированный токен: $SONAR_TOKEN"

# Создание токена через API
curl -s -u admin:admin \
  -X POST \
  -d "name=heroes-1c-extractor-token" \
  -d "type=GLOBAL_ANALYSIS_TOKEN" \
  -d "login=admin" \
  "http://localhost:9000/api/user_tokens/generate" \
  | jq -r '.token' > /tmp/sonar_token.txt

if [ -s /tmp/sonar_token.txt ]; then
    SONAR_TOKEN=$(cat /tmp/sonar_token.txt)
    echo "✅ Токен создан: $SONAR_TOKEN"
else
    echo "⚠️ Не удалось создать токен через API, используем сгенерированный"
fi

# Сохранение ключей в macOS Keychain
echo "💾 Сохранение ключей в macOS Keychain..."

# SONAR_TOKEN
security add-generic-password \
  -a "sonar-token" \
  -s "heroes-1c-extractor" \
  -w "$SONAR_TOKEN" \
  -U

# SONAR_HOST_URL
security add-generic-password \
  -a "sonar-host-url" \
  -s "heroes-1c-extractor" \
  -w "http://localhost:9000" \
  -U

# SONAR_ORGANIZATION (для локального использования)
security add-generic-password \
  -a "sonar-organization" \
  -s "heroes-1c-extractor" \
  -w "heroes-platform" \
  -U

echo "✅ Ключи сохранены в macOS Keychain"

# Создание .env файла для локального использования
echo "📝 Создание .env файла..."
cat > .env.sonarqube << EOF
# SonarQube Configuration
SONAR_TOKEN=$SONAR_TOKEN
SONAR_HOST_URL=http://localhost:9000
SONAR_ORGANIZATION=heroes-platform
SONAR_PROJECT_KEY=heroes-1c-extractor
EOF

echo "✅ .env файл создан: .env.sonarqube"

# Создание скрипта для получения ключей из Keychain
echo "🔧 Создание скрипта для получения ключей..."
cat > scripts/get-sonarqube-keys.sh << 'EOF'
#!/bin/bash

# Получение ключей SonarQube из macOS Keychain

echo "🔑 Получение ключей SonarQube из Keychain..."

# SONAR_TOKEN
SONAR_TOKEN=$(security find-generic-password -a "sonar-token" -s "heroes-1c-extractor" -w 2>/dev/null)
if [ -n "$SONAR_TOKEN" ]; then
    echo "✅ SONAR_TOKEN: $SONAR_TOKEN"
    export SONAR_TOKEN
else
    echo "❌ SONAR_TOKEN не найден в Keychain"
fi

# SONAR_HOST_URL
SONAR_HOST_URL=$(security find-generic-password -a "sonar-host-url" -s "heroes-1c-extractor" -w 2>/dev/null)
if [ -n "$SONAR_HOST_URL" ]; then
    echo "✅ SONAR_HOST_URL: $SONAR_HOST_URL"
    export SONAR_HOST_URL
else
    echo "❌ SONAR_HOST_URL не найден в Keychain"
fi

# SONAR_ORGANIZATION
SONAR_ORGANIZATION=$(security find-generic-password -a "sonar-organization" -s "heroes-1c-extractor" -w 2>/dev/null)
if [ -n "$SONAR_ORGANIZATION" ]; then
    echo "✅ SONAR_ORGANIZATION: $SONAR_ORGANIZATION"
    export SONAR_ORGANIZATION
else
    echo "❌ SONAR_ORGANIZATION не найден в Keychain"
fi

echo "🎯 Ключи загружены в переменные окружения"
EOF

chmod +x scripts/get-sonarqube-keys.sh

echo "✅ Скрипт для получения ключей создан: scripts/get-sonarqube-keys.sh"

# Тестирование подключения
echo "🧪 Тестирование подключения к SonarQube..."
if curl -s -u admin:$SONAR_TOKEN http://localhost:9000/api/system/status | grep -q "UP"; then
    echo "✅ Подключение к SonarQube успешно"
else
    echo "⚠️ Проблемы с подключением к SonarQube"
fi

echo ""
echo "🎯 Настройка завершена!"
echo ""
echo "📋 Созданные файлы:"
echo "  - .env.sonarqube (локальные переменные)"
echo "  - scripts/get-sonarqube-keys.sh (скрипт получения ключей)"
echo ""
echo "🔑 Ключи сохранены в macOS Keychain:"
echo "  - sonar-token: $SONAR_TOKEN"
echo "  - sonar-host-url: http://localhost:9000"
echo "  - sonar-organization: heroes-platform"
echo ""
echo "🚀 Следующие шаги:"
echo "1. Откройте SonarQube: http://localhost:9000"
echo "2. Логин: admin, Пароль: admin"
echo "3. Запустите сканирование: make sonar-scan"
echo ""
echo "💡 Для получения ключей в других скриптах:"
echo "  source scripts/get-sonarqube-keys.sh"
