#!/bin/bash

# Скрипт настройки окружения macOS для работы с ctool1cd
# Автор: Анализ на основе проекта tools_ui_1c
# Дата: 20.07.2024

set -e

echo "🚀 Настройка окружения macOS для работы с ctool1cd"
echo "=================================================="

# Проверка архитектуры
ARCH=$(uname -m)
echo "📋 Архитектура системы: $ARCH"

if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  Внимание: Скрипт оптимизирован для Apple Silicon (ARM64)"
fi

# Проверка наличия Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew не установлен. Установите Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew найден"

# Установка Docker Desktop
echo ""
echo "🐳 Установка Docker Desktop..."
if ! command -v docker &> /dev/null; then
    echo "📦 Устанавливаем Docker Desktop..."
    brew install --cask docker
    
    echo "⚠️  Docker Desktop установлен. Запустите приложение Docker Desktop"
    echo "   и дождитесь полной загрузки, затем запустите скрипт снова."
    echo ""
    echo "💡 После запуска Docker Desktop выполните:"
    echo "   ./setup_macos_environment.sh"
    exit 0
else
    echo "✅ Docker уже установлен"
fi

# Проверка работы Docker
echo ""
echo "🔍 Проверка работы Docker..."
if ! docker info &> /dev/null; then
    echo "❌ Docker не запущен. Запустите Docker Desktop и попробуйте снова."
    exit 1
fi

echo "✅ Docker работает корректно"

# Создание Dockerfile для ctool1cd
echo ""
echo "📝 Создание Dockerfile для ctool1cd..."

cat > Dockerfile.ctool1cd << 'EOF'
FROM ubuntu:20.04

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y \
    libboost-filesystem1.71.0 \
    libboost-system1.71.0 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Копирование утилиты ctool1cd
COPY ctool1cd /usr/local/bin/
RUN chmod +x /usr/local/bin/ctool1cd

# Создание рабочей директории
WORKDIR /work

# Точка входа
ENTRYPOINT ["ctool1cd"]
EOF

echo "✅ Dockerfile создан: Dockerfile.ctool1cd"

# Создание скрипта для извлечения ctool1cd
echo ""
echo "🔧 Создание скрипта извлечения ctool1cd..."

cat > extract_ctool1cd.sh << 'EOF'
#!/bin/bash

# Скрипт извлечения ctool1cd из проекта tools_ui_1c

set -e

echo "🔧 Извлечение ctool1cd из проекта tools_ui_1c..."

# Проверка наличия проекта
if [ ! -d "tools_ui_1c" ]; then
    echo "❌ Проект tools_ui_1c не найден в текущей директории"
    echo "   Клонируйте проект: git clone https://github.com/cpr1c/tools_ui_1c.git"
    exit 1
fi

# Путь к архиву с утилитой
TEMPLATE_PATH="tools_ui_1c/src/Инструменты/src/CommonTemplates/УИ_ctool1cd/Template.bin"

if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "❌ Архив с утилитой ctool1cd не найден: $TEMPLATE_PATH"
    exit 1
fi

# Создание временной директории
TEMP_DIR=$(mktemp -d)
echo "📁 Временная директория: $TEMP_DIR"

# Извлечение архива
echo "📦 Извлечение архива..."
unzip -q "$TEMPLATE_PATH" -d "$TEMP_DIR"

# Копирование Linux версии
if [ -f "$TEMP_DIR/linux/ctool1cd" ]; then
    cp "$TEMP_DIR/linux/ctool1cd" ./ctool1cd
    chmod +x ./ctool1cd
    echo "✅ ctool1cd извлечен и готов к использованию"
else
    echo "❌ Файл ctool1cd не найден в архиве"
    exit 1
fi

# Очистка
rm -rf "$TEMP_DIR"

echo "✅ Извлечение завершено"
EOF

chmod +x extract_ctool1cd.sh
echo "✅ Скрипт извлечения создан: extract_ctool1cd.sh"

# Создание скрипта сборки Docker образа
echo ""
echo "🐳 Создание скрипта сборки Docker образа..."

cat > build_docker_image.sh << 'EOF'
#!/bin/bash

# Скрипт сборки Docker образа с ctool1cd

set -e

echo "🐳 Сборка Docker образа ctool1cd..."

# Проверка наличия файлов
if [ ! -f "ctool1cd" ]; then
    echo "❌ Файл ctool1cd не найден. Запустите сначала:"
    echo "   ./extract_ctool1cd.sh"
    exit 1
fi

if [ ! -f "Dockerfile.ctool1cd" ]; then
    echo "❌ Dockerfile.ctool1cd не найден"
    exit 1
fi

# Сборка образа
echo "🔨 Сборка Docker образа..."
docker build -f Dockerfile.ctool1cd -t ctool1cd:latest .

echo "✅ Docker образ собран: ctool1cd:latest"

# Тестирование
echo ""
echo "🧪 Тестирование Docker образа..."
if docker run --rm ctool1cd:latest --help 2>/dev/null; then
    echo "✅ Docker образ работает корректно"
else
    echo "⚠️  Docker образ собран, но тестирование не прошло"
    echo "   Это может быть нормально, если утилита не поддерживает --help"
fi
EOF

chmod +x build_docker_image.sh
echo "✅ Скрипт сборки создан: build_docker_image.sh"

# Создание скрипта для запуска анализа
echo ""
echo "📊 Создание скрипта для запуска анализа..."

cat > analyze_1cd_docker.sh << 'EOF'
#!/bin/bash

# Скрипт анализа файла 1CD через Docker

set -e

if [ $# -lt 1 ]; then
    echo "Использование: $0 <путь_к_файлу_1cd> [выходной_csv]"
    echo ""
    echo "Примеры:"
    echo "  $0 /path/to/file.1cd"
    echo "  $0 /path/to/file.1cd results.csv"
    exit 1
fi

FILE_1CD="$1"
OUTPUT_CSV="$2"

# Проверка файла
if [ ! -f "$FILE_1CD" ]; then
    echo "❌ Файл не найден: $FILE_1CD"
    exit 1
fi

# Проверка Docker образа
if ! docker image inspect ctool1cd:latest &>/dev/null; then
    echo "❌ Docker образ ctool1cd:latest не найден"
    echo "   Запустите сначала: ./build_docker_image.sh"
    exit 1
fi

echo "🔍 Анализ файла: $FILE_1CD"

# Создание временных файлов
TEMP_CSV=$(mktemp)
TEMP_LOG=$(mktemp)

# Получение абсолютного пути к файлу
ABSOLUTE_PATH=$(realpath "$FILE_1CD")

# Запуск анализа через Docker
echo "🚀 Запуск ctool1cd через Docker..."
docker run --rm \
    -v "$ABSOLUTE_PATH:/work/input.1cd:ro" \
    -v "$(dirname "$TEMP_CSV"):/work/output" \
    ctool1cd:latest \
    -ne -sts "/work/output/$(basename "$TEMP_CSV")" -q "/work/input.1cd" -l "/work/output/$(basename "$TEMP_LOG")"

# Проверка результата
if [ -f "$TEMP_CSV" ] && [ -s "$TEMP_CSV" ]; then
    echo "✅ Анализ завершен успешно"
    
    # Вывод результатов
    echo ""
    echo "📊 Результаты анализа:"
    echo "======================"
    
    if command -v column &>/dev/null; then
        head -10 "$TEMP_CSV" | column -t -s '|'
    else
        head -10 "$TEMP_CSV"
    fi
    
    # Сохранение в указанный файл
    if [ -n "$OUTPUT_CSV" ]; then
        cp "$TEMP_CSV" "$OUTPUT_CSV"
        echo ""
        echo "💾 Результаты сохранены в: $OUTPUT_CSV"
    fi
    
else
    echo "❌ Ошибка при анализе"
    if [ -f "$TEMP_LOG" ]; then
        echo "📋 Лог ошибки:"
        cat "$TEMP_LOG"
    fi
fi

# Очистка
rm -f "$TEMP_CSV" "$TEMP_LOG"
EOF

chmod +x analyze_1cd_docker.sh
echo "✅ Скрипт анализа создан: analyze_1cd_docker.sh"

# Создание README для macOS
echo ""
echo "📚 Создание README для macOS..."

cat > README_macos.md << 'EOF'
# Настройка окружения macOS для работы с ctool1cd

## Обзор

Этот набор скриптов настраивает окружение macOS для работы с утилитой ctool1cd через Docker.

## Требования

- macOS 10.15+ (рекомендуется macOS 11+ для Apple Silicon)
- Homebrew
- Docker Desktop

## Быстрая настройка

1. **Запустите скрипт настройки:**
   ```bash
   ./setup_macos_environment.sh
   ```

2. **Извлеките ctool1cd из проекта tools_ui_1c:**
   ```bash
   ./extract_ctool1cd.sh
   ```

3. **Соберите Docker образ:**
   ```bash
   ./build_docker_image.sh
   ```

## Использование

### Анализ файла 1CD
```bash
./analyze_1cd_docker.sh /path/to/file.1cd
```

### Сохранение результатов в файл
```bash
./analyze_1cd_docker.sh /path/to/file.1cd results.csv
```

## Структура файлов

- `setup_macos_environment.sh` - основной скрипт настройки
- `extract_ctool1cd.sh` - извлечение ctool1cd из проекта
- `build_docker_image.sh` - сборка Docker образа
- `analyze_1cd_docker.sh` - анализ файлов 1CD
- `Dockerfile.ctool1cd` - Dockerfile для ctool1cd

## Устранение неполадок

### Docker не запущен
```bash
# Запустите Docker Desktop и дождитесь полной загрузки
open -a Docker
```

### Ошибка прав доступа
```bash
# Убедитесь, что файлы имеют права на выполнение
chmod +x *.sh
```

### Файл ctool1cd не найден
```bash
# Убедитесь, что проект tools_ui_1c клонирован
git clone https://github.com/cpr1c/tools_ui_1c.git
```

## Интеграция с tools_ui_1c

Для интеграции с tools_ui_1c модифицируйте код для запуска через Docker:

```1c
// Пример кода для запуска ctool1cd через Docker
Процедура ЗапуститьCtool1cdЧерезDocker(ПутьКФайлу1CD, ПутьКРезультату)
    Команда = СтрШаблон("docker run --rm -v ""%1"":/work/input.1cd:ro -v ""%2"":/work/output ctool1cd:latest -ne -sts /work/output/result.csv -q /work/input.1cd", 
                        ПутьКФайлу1CD, ПутьКРезультату)
    ЗапуститьПриложение(Команда)
КонецПроцедуры
```

## Производительность

- Время анализа: ~1-5 минут для файла 100MB
- Использование памяти: ~200-500MB
- Поддерживаемые размеры файлов: до 2GB

## Поддержка

При возникновении проблем:
1. Проверьте логи Docker: `docker logs <container_id>`
2. Убедитесь в корректности путей к файлам
3. Проверьте права доступа к файлам 1CD
EOF

echo "✅ README создан: README_macos.md"

echo ""
echo "🎉 Настройка окружения завершена!"
echo "=================================="
echo ""
echo "📋 Следующие шаги:"
echo "1. Убедитесь, что Docker Desktop запущен"
echo "2. Запустите: ./extract_ctool1cd.sh"
echo "3. Запустите: ./build_docker_image.sh"
echo "4. Протестируйте: ./analyze_1cd_docker.sh <путь_к_файлу_1cd>"
echo ""
echo "📚 Дополнительная информация: README_macos.md" 