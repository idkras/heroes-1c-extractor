#!/bin/bash

# Скрипт для запуска ctool1cd на Mac M2 через Docker
# Использует x86_64 эмуляцию через Rosetta

set -e

echo "🚀 Запуск ctool1cd для анализа 1CD файла на Mac M2"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

# Проверяем наличие файла
if [ ! -f "raw/1Cv8.1CD" ]; then
    echo "❌ Файл raw/1Cv8.1CD не найден"
    exit 1
fi

echo "📁 Анализируемый файл: raw/1Cv8.1CD"
echo "📏 Размер файла: $(du -h raw/1Cv8.1CD | cut -f1)"

# Создаем директории для результатов
mkdir -p docs/reports
mkdir -p docs/logs

echo "🔧 Запуск ctool1cd через Docker с x86_64 эмуляцией..."

# Запускаем Ubuntu контейнер с x86_64 архитектурой
docker run --rm \
    --platform linux/amd64 \
    -v "$(pwd):/workspace" \
    -w /workspace \
    ubuntu:22.04 \
    bash -c "
        # Обновляем пакеты
        apt-get update -qq
        
        # Добавляем репозиторий e8tools
        apt-get install -y software-properties-common
        add-apt-repository ppa:dmpas/e8 -y
        apt-get update -qq
        
        # Устанавливаем ctool1cd
        apt-get install -y ctool1cd
        
        echo '✅ ctool1cd установлен'
        
        # Анализируем файл
        echo '🔍 Начинаем анализ 1CD файла...'
        ctool1cd -ne -sts docs/reports/ctool1cd_analysis.csv -q raw/1Cv8.1CD -l docs/logs/ctool1cd_analysis.log
        
        echo '✅ Анализ завершен'
    "

echo "📊 Результаты сохранены в:"
echo "   - docs/reports/ctool1cd_analysis.csv"
echo "   - docs/logs/ctool1cd_analysis.log" 