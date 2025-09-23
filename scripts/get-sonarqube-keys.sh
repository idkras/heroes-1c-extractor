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
