#!/bin/bash

# Улучшенный скрипт для запуска ctool1cd на Mac M2
# С полной обработкой ошибок и альтернативными путями

set -e

echo "🚀 РОБУСТНЫЙ ЗАПУСК ctool1cd для анализа 1CD файла"

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    echo "Установите Docker Desktop для Mac"
    exit 1
fi

# Проверяем, что Docker работает
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен"
    echo "Запустите Docker Desktop"
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

# Функция для очистки при ошибке
cleanup() {
    echo "🧹 Очистка временных файлов..."
    docker system prune -f &> /dev/null || true
}

trap cleanup EXIT

# Проверяем существование образа
if ! docker image inspect ctool1cd-ubuntu:latest &> /dev/null; then
    echo "🔧 Создаем Docker образ с ctool1cd..."
    
    # Создаем Dockerfile с улучшенной обработкой ошибок
    cat > Dockerfile.ctool1cd << 'EOF'
FROM ubuntu:22.04

# Устанавливаем необходимые пакеты с обработкой ошибок
RUN apt-get update -qq && \
    apt-get install -y software-properties-common wget unzip curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Пробуем разные способы установки ctool1cd
RUN set -e; \
    # Способ 1: PPA репозиторий
    if add-apt-repository ppa:dmpas/e8 -y && apt-get update -qq && apt-get install -y ctool1cd; then \
        echo "✅ ctool1cd установлен через PPA"; \
    # Способ 2: Скачивание бинарника
    elif wget -O /usr/local/bin/ctool1cd "https://github.com/e8tools/tool1cd/releases/latest/download/ctool1cd-linux-x64" && \
         chmod +x /usr/local/bin/ctool1cd; then \
        echo "✅ ctool1cd установлен из бинарника"; \
    # Способ 3: Компиляция из исходников
    elif apt-get install -y build-essential cmake git && \
         git clone https://github.com/e8tools/tool1cd.git && \
         cd tool1cd && mkdir build && cd build && \
         cmake .. && make && make install; then \
        echo "✅ ctool1cd скомпилирован из исходников"; \
    else \
        echo "❌ Не удалось установить ctool1cd"; \
        exit 1; \
    fi

# Создаем рабочую директорию
WORKDIR /workspace

# Команда по умолчанию
CMD ["ctool1cd", "--help"]
EOF

    # Собираем образ с таймаутом
    echo "⏱️  Сборка образа (может занять 10-15 минут)..."
    timeout 1800 docker build -f Dockerfile.ctool1cd -t ctool1cd-ubuntu:latest . || {
        echo "❌ Таймаут сборки образа"
        exit 1
    }
    rm Dockerfile.ctool1cd
    
    echo "✅ Docker образ создан"
else
    echo "✅ Docker образ уже существует"
fi

echo "🔍 Запуск анализа 1CD файла..."
echo "⚠️  Это может занять 30-60 минут для файла 81GB..."

# Запускаем анализ с обработкой ошибок
if docker run --rm \
    --platform linux/amd64 \
    --memory=4g \
    --cpus=2 \
    -v "$(pwd):/workspace" \
    -w /workspace \
    ctool1cd-ubuntu:latest \
    ctool1cd -ne -sts docs/reports/ctool1cd_analysis.csv -q raw/1Cv8.1CD -l docs/logs/ctool1cd_analysis.log; then
    
    echo "✅ Анализ завершен успешно"
    echo "📊 Результаты сохранены в:"
    echo "   - docs/reports/ctool1cd_analysis.csv"
    echo "   - docs/logs/ctool1cd_analysis.log"
else
    echo "❌ Ошибка при анализе"
    echo "🔍 Проверяем логи..."
    if [ -f "docs/logs/ctool1cd_analysis.log" ]; then
        tail -20 docs/logs/ctool1cd_analysis.log
    fi
    exit 1
fi 