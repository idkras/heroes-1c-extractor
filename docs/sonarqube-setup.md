# SonarQube Setup для Heroes 1C Extractor

## 🎯 Обзор

SonarQube интегрирован в проект для автоматического статического анализа кода, выявления уязвимостей, багов и "code smells".

## 🚀 Быстрый старт

### Локальный запуск SonarQube

```bash
# Запуск SonarQube локально
make sonar-local

# Запуск сканирования кода
make sonar-scan

# Остановка SonarQube
make sonar-stop
```

### Веб-интерфейс

- **URL**: http://localhost:9000
- **Логин**: admin
- **Пароль**: admin

## 📋 Команды Makefile

| Команда | Описание |
|---------|----------|
| `make sonar-local` | Запустить локальный SonarQube |
| `make sonar-scan` | Запустить сканирование кода |
| `make sonar-stop` | Остановить SonarQube |
| `make sonar-clean` | Очистить данные SonarQube |
| `make security-scan` | Сканирование безопасности |
| `make quality-check` | Полная проверка качества |

## 🔧 Конфигурация

### sonar-project.properties

Основные настройки проекта:
- **Ключ проекта**: `heroes-1c-extractor`
- **Источники**: `src/`
- **Тесты**: `tests/`
- **Исключения**: временные файлы, данные, инструменты

### Docker Compose

SonarQube запускается в Docker с PostgreSQL:
- **SonarQube**: порт 9000
- **PostgreSQL**: порт 5432
- **Volumes**: данные сохраняются между перезапусками

## 🔒 Безопасность

### Bandit (Python Security)

```bash
# Сканирование безопасности
bandit -r src/ -f json -o bandit-report.json
```

### Safety (Dependencies)

```bash
# Проверка уязвимостей в зависимостях
safety check --json --output safety-report.json
```

## 🎯 Quality Gates

### Критерии прохождения

- **Покрытие тестами**: ≥ 80%
- **Дублирование кода**: ≤ 3%
- **Технический долг**: ≤ 30 минут
- **Критические уязвимости**: 0
- **Критические баги**: 0
- **Code smells**: ≤ 10
- **Сложность**: ≤ 100
- **Поддерживаемость**: рейтинг A или B

## 🚀 CI/CD Integration

### GitHub Actions

Автоматический анализ при:
- Push в main/develop
- Pull Request в main/develop

### Workflow Steps

1. **Checkout code**
2. **Setup Python 3.11**
3. **Install dependencies**
4. **Run tests with coverage**
5. **Security scan (Bandit + Safety)**
6. **SonarQube analysis**
7. **Quality Gate check**

## 📊 Отчеты

### Покрытие тестами
- **Файл**: `coverage.xml`
- **HTML**: `htmlcov/index.html`

### Безопасность
- **Bandit**: `bandit-report.json`
- **Safety**: `safety-report.json`

### Тесты
- **JUnit**: `test-results.xml`

## 🔍 Анализ кода

### Что анализируется

- **Bugs**: ошибки в коде
- **Vulnerabilities**: уязвимости безопасности
- **Code Smells**: подозрительные конструкции
- **Duplications**: дублирование кода
- **Coverage**: покрытие тестами
- **Complexity**: сложность кода

### Исключения

Следующие директории исключены из анализа:
- `__pycache__/`
- `.venv/`
- `data/raw/`
- `data/exported/`
- `tools/`
- `notebooks/`
- `temp/`

## 🛠️ Troubleshooting

### Проблемы с запуском

```bash
# Очистка и перезапуск
make sonar-clean
make sonar-local
```

### Проблемы с памятью

```bash
# Увеличение памяти для Docker
export SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
```

### Проблемы с портами

```bash
# Проверка занятых портов
lsof -i :9000
lsof -i :5432
```

## 📚 Дополнительные ресурсы

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarQube Python Plugin](https://docs.sonarqube.org/latest/analysis/languages/python/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Safety Documentation](https://pyup.io/safety/)

## 🎯 Best Practices

1. **Регулярный анализ**: запускайте анализ после каждого значительного изменения
2. **Quality Gates**: не мержите код, не прошедший Quality Gate
3. **Безопасность**: исправляйте критические уязвимости немедленно
4. **Покрытие**: поддерживайте покрытие тестами ≥ 80%
5. **Дублирование**: избегайте дублирования кода
6. **Сложность**: разбивайте сложные функции на более простые
