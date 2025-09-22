# DeepSource + Cursor AI Agent Integration Guide

## 🎯 Цель интеграции

Автоматические проверки качества кода в PR + полуавтоматическое исправление замечаний через Cursor AI Agent.

## 📋 Быстрый старт

### 1. Установка и настройка

```bash
# Установка pre-commit хуков
make install-pre-commit

# Локальная проверка DeepSource
make deepsource-local
```

### 2. GitHub интеграция

1. **Авторизация в DeepSource:**
   - Зайти на [deepsource.io](https://deepsource.io)
   - Авторизоваться через GitHub
   - Установить GitHub App на организацию/репозиторий

2. **Настройка Branch Protection:**
   - GitHub → Settings → Branches → main
   - Включить "Require status checks to pass before merging"
   - Добавить "DeepSource" в список обязательных проверок

### 3. Конфигурация

**Файл `.deepsource.toml`** уже настроен с:
- Python анализатор (runtime 3.11)
- JavaScript анализатор (Node.js 20)
- Поиск секретов
- Исключения для legacy кода
- Quality gate настройки

**Файл `.pre-commit-config.yaml`** включает:
- Black форматирование
- isort сортировка импортов
- flake8 линтинг
- mypy типизация
- bandit безопасность
- detect-secrets поиск секретов

## 🤖 Использование с Cursor AI Agent

### Команды для Cursor AI Agent

```markdown
# Привести код к стандартам проекта
"Приведи код к правилам Black/Flake8/Isort (см. pyproject.toml), не меняя публичные интерфейсы."

# Исправить предупреждения DeepSource
"Исправь предупреждения DeepSource из последнего PR, предложи минимальный дифф."

# Автоматическое исправление
"Запусти авто-фикс ESLint/Prettier и объясни, какие правила сработали."

# Анализ замечаний
"Проанализируй замечания DeepSource в последнем PR и сгруппируй по типам, предложи план рефакторинга на 3 итерации."

# Генерация pre-commit хуков
"Сгенерируй pre-commit хуки под наш стек и добавь инструкции в README."
```

### Workflow с Cursor AI Agent

1. **Перед коммитом:**
   ```bash
   make pre-commit
   ```

2. **Если есть ошибки:**
   - Попросить Cursor AI Agent исправить
   - Использовать команды выше

3. **После исправления:**
   ```bash
   make deepsource-local  # Локальная проверка
   git add .
   git commit -m "fix: исправлены замечания DeepSource"
   ```

4. **В PR:**
   - DeepSource автоматически проверит код
   - При ошибках - использовать Cursor AI Agent для исправления

## 🔧 Локальные команды

```bash
# Установка pre-commit
make install-pre-commit

# Локальная проверка (аналог DeepSource)
make deepsource-local

# Форматирование кода
make format

# Линтинг
make lint

# Автоисправление
make auto-fix

# Полная проверка качества
make quality-check
```

## 📊 Quality Gate настройки

**Текущие настройки в `.deepsource.toml`:**
- ✅ Блокировка PR при критичных проблемах
- ❌ НЕ блокировка при стилевых замечаниях
- 📊 Минимальное покрытие: 80% (новые файлы), 70% (измененные)

## 🚫 Исключения

**Автоматически игнорируются:**
- `__pycache__/`, `node_modules/`, `build/`, `dist/`
- `temp/`, `logs/`, `data/raw/`, `data/exported/`
- `patches/`, `tools/`, `dck1c/`
- Сгенерированные файлы и отчеты

## 🔍 Отладка проблем

### Если DeepSource не запускается:
1. Проверить `.deepsource.toml` в корне репозитория
2. Убедиться, что GitHub App установлен
3. Проверить Branch Protection настройки

### Если pre-commit не работает:
```bash
# Переустановка хуков
pre-commit uninstall
pre-commit install

# Принудительный запуск
pre-commit run --all-files
```

### Если Cursor AI Agent не понимает контекст:
- Указать конкретные файлы конфигурации
- Ссылаться на существующие примеры в коде
- Просить объяснить, какие правила сработали

## 📈 Метрики успеха

- **70-90%** снижение ручных правок в PR
- **Автоматические комментарии** DeepSource в PR
- **Quality gate** блокирует PR при критичных проблемах
- **Локальная проверка** предотвращает проблемы до PR

## 🔄 Постепенное ужесточение

1. **Неделя 1:** Базовые проверки (Black, isort, flake8)
2. **Неделя 2:** Добавить mypy типизацию
3. **Неделя 3:** Включить bandit безопасность
4. **Неделя 4:** Настроить покрытие тестов

## 📚 Дополнительные ресурсы

- [DeepSource Documentation](https://deepsource.io/docs)
- [Pre-commit Hooks](https://pre-commit.com/hooks.html)
- [Cursor AI Agent Guide](https://docs.cursor.com/ai)
- [Python Code Quality Tools](https://python.org/dev/peps/pep-0008/)

## 🆘 Поддержка

При проблемах:
1. Проверить логи: `make pre-commit`
2. Обратиться к Cursor AI Agent с конкретной ошибкой
3. Проверить настройки в `.deepsource.toml`
4. Убедиться в корректности GitHub интеграции
