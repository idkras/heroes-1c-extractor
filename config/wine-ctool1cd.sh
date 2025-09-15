#!/bin/bash

# Wine скрипт для запуска ctool1cd на Mac M2
# Использует Wine для запуска Windows версии ctool1cd

set -e

echo "🍷 Запуск ctool1cd через Wine на Mac M2..."

# Проверяем наличие Wine
if ! command -v wine &> /dev/null; then
    echo "❌ Wine не установлен. Устанавливаем..."
    brew install --cask wine-stable
fi

# Создаем необходимые директории
mkdir -p docs/reports docs/logs

# Скачиваем Windows версию ctool1cd если её нет
if [ ! -f "ctool1cd.exe" ]; then
    echo "📥 Скачиваем Windows версию ctool1cd..."
    curl -L -o ctool1cd.exe "https://github.com/e8tools/tool1cd/releases/download/v1.0.0/ctool1cd-win-x64.exe"
fi

echo "🚀 Запуск анализа 1CD файла через Wine..."
wine ctool1cd.exe -ne -sts docs/reports/ctool1cd_analysis.csv -q raw/1Cv8.1CD -l docs/logs/ctool1cd_analysis.log

echo "✅ Анализ завершен успешно!"
echo "📊 Результаты сохранены в:"
echo "   - docs/reports/ctool1cd_analysis.csv"
echo "   - docs/logs/ctool1cd_analysis.log" 