#!/bin/bash

# Скрипт для запуска ctool1cd на Mac M2
# Использует Wine для запуска Windows версии ctool1cd

set -e

echo "🍷 Запуск ctool1cd через Wine на Mac M2..."

# Проверяем наличие Wine
if ! command -v wine &> /dev/null; then
    echo "❌ Wine не установлен. Устанавливаем..."
    brew install --cask wine@staging
fi

# Проверяем наличие ctool1cd.exe
if [ ! -f "tool1cd/bin/ctool1cd.exe" ]; then
    echo "❌ ctool1cd.exe не найден. Скачиваем..."
    wget https://github.com/e8tools/tool1cd/releases/download/v1.0.0-beta2/tool1cd-1.0.0.10.zip
    unzip tool1cd-1.0.0.10.zip
fi

# Создаем необходимые директории
mkdir -p docs/reports docs/logs

# Устанавливаем переменные окружения для Wine
export WINEPREFIX="$HOME/.wine"
export WINEARCH=win64

# Инициализируем Wine если нужно
if [ ! -d "$WINEPREFIX" ]; then
    echo "🔧 Инициализация Wine..."
    wineboot --init
fi

echo "🚀 Запуск анализа 1CD файла..."
cd tool1cd/bin

# Запускаем ctool1cd с параметрами
wine ctool1cd.exe -ne -sts ../../../docs/reports/ctool1cd_analysis.csv -q ../../../raw/1Cv8.1CD -l ../../../docs/logs/ctool1cd_analysis.log

echo "✅ Анализ завершен успешно!" 