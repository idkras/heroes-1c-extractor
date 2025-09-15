#!/bin/bash

# Оптимизированный Docker скрипт для сборки ctool1cd из исходников
# Использует флаг NOGUI для исключения GUI компонентов

set -e

echo "🔧 Сборка ctool1cd из исходников с флагом NOGUI..."

# Создаем Docker образ если его нет
if ! docker image inspect ctool1cd-ubuntu:latest &> /dev/null; then
    echo "📦 Создание Docker образа ctool1cd-ubuntu..."
    docker build -f Dockerfile.ctool1cd -t ctool1cd-ubuntu:latest .
fi

# Создаем необходимые директории
mkdir -p docs/reports docs/logs

echo "🚀 Запуск анализа 1CD файла..."
docker run --rm \
    --platform linux/amd64 \
    -v "$(pwd):/workspace" \
    -w /workspace \
    ctool1cd-ubuntu:latest \
    ctool1cd -ne -sts docs/reports/ctool1cd_analysis.csv -q raw/1Cv8.1CD -l docs/logs/ctool1cd_analysis.log

echo "✅ Анализ завершен успешно!"
echo "📊 Результаты сохранены в docs/reports/ctool1cd_analysis.csv"
echo "📝 Логи сохранены в docs/logs/ctool1cd_analysis.log" 