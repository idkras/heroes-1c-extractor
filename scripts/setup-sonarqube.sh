#!/bin/bash

# SonarQube Setup Script for Heroes 1C Extractor
# Автоматическая настройка SonarQube для проекта

set -e

echo "🚀 Настройка SonarQube для Heroes 1C Extractor"
echo "=============================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создание директории для SonarQube
echo "📁 Создание директорий..."
mkdir -p .sonarqube
mkdir -p .github/workflows

# Проверка существующих файлов
echo "🔍 Проверка конфигурации..."

if [ ! -f "sonar-project.properties" ]; then
    echo "❌ Файл sonar-project.properties не найден"
    exit 1
fi

if [ ! -f "docker-compose.sonarqube.yml" ]; then
    echo "❌ Файл docker-compose.sonarqube.yml не найден"
    exit 1
fi

if [ ! -f ".github/workflows/sonarqube.yml" ]; then
    echo "❌ Файл .github/workflows/sonarqube.yml не найден"
    exit 1
fi

# Установка зависимостей для безопасности
echo "📦 Установка зависимостей для безопасности..."
pip install bandit safety

# Создание .gitignore для SonarQube
echo "📝 Настройка .gitignore..."
if ! grep -q "sonar" .gitignore 2>/dev/null; then
    cat >> .gitignore << EOF

# SonarQube
.scannerwork/
sonar-project.properties.bak
bandit-report.json
safety-report.json
EOF
fi

# Создание скрипта для локального тестирования
echo "🧪 Создание скрипта для тестирования..."
cat > scripts/test-sonarqube.sh << 'EOF'
#!/bin/bash

echo "🧪 Тестирование SonarQube конфигурации"
echo "======================================="

# Проверка файлов конфигурации
echo "📋 Проверка файлов конфигурации..."
required_files=(
    "sonar-project.properties"
    "docker-compose.sonarqube.yml"
    ".github/workflows/sonarqube.yml"
    ".sonarqube/quality-gate.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - НЕ НАЙДЕН"
        exit 1
    fi
done

# Проверка Docker
echo "🐳 Проверка Docker..."
if command -v docker &> /dev/null; then
    echo "✅ Docker установлен"
else
    echo "❌ Docker не установлен"
    exit 1
fi

# Проверка зависимостей Python
echo "🐍 Проверка зависимостей Python..."
python -c "import bandit, safety" 2>/dev/null && echo "✅ Bandit и Safety установлены" || echo "❌ Bandit или Safety не установлены"

echo "🎯 Все проверки пройдены успешно!"
EOF

chmod +x scripts/test-sonarqube.sh

# Создание README для SonarQube
echo "📚 Создание документации..."
cat > docs/sonarqube-quickstart.md << 'EOF'
# SonarQube Quick Start

## 🚀 Быстрый запуск

### 1. Локальный запуск
```bash
# Запуск SonarQube
make sonar-local

# Открыть в браузере
open http://localhost:9000
# Логин: admin, Пароль: admin
```

### 2. Сканирование кода
```bash
# Запуск сканирования
make sonar-scan

# Проверка безопасности
make security-scan
```

### 3. Остановка
```bash
# Остановка SonarQube
make sonar-stop

# Очистка данных
make sonar-clean
```

## 🔧 Настройка GitHub Secrets

Для работы с GitHub Actions добавьте в Secrets:

- `SONAR_TOKEN`: токен из SonarQube
- `SONAR_HOST_URL`: URL сервера SonarQube
- `SONAR_ORGANIZATION`: организация (для SonarCloud)

## 📊 Quality Gates

Проект настроен с следующими критериями:
- Покрытие тестами: ≥ 80%
- Дублирование кода: ≤ 3%
- Технический долг: ≤ 30 минут
- Критические уязвимости: 0
- Критические баги: 0

## 🆘 Troubleshooting

### Проблемы с портами
```bash
# Проверка занятых портов
lsof -i :9000
lsof -i :5432
```

### Очистка и перезапуск
```bash
make sonar-clean
make sonar-local
```
EOF

echo "✅ Настройка SonarQube завершена!"
echo ""
echo "🎯 Следующие шаги:"
echo "1. Запустите: make sonar-local"
echo "2. Откройте: http://localhost:9000"
echo "3. Логин: admin, Пароль: admin"
echo "4. Запустите: make sonar-scan"
echo ""
echo "📚 Документация:"
echo "- docs/sonarqube-setup.md"
echo "- docs/sonarqube-cicd-diagram.md"
echo "- docs/sonarqube-quickstart.md"
echo ""
echo "🧪 Тестирование:"
echo "- scripts/test-sonarqube.sh"
