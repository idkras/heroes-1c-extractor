# 🚀 Heroes Platform - Быстрый старт

## Одна команда для установки всего

При переносе `heroes-platform` в новый проект, просто запустите:

### Unix/Linux/macOS:
```bash
cd heroes-platform
./install.sh
```

### Windows:
```cmd
cd heroes-platform
install.bat
```

### Альтернативные способы:

**Make:**
```bash
cd heroes-platform
make setup
```

**npm:**
```bash
cd heroes-platform
npm run setup
```

**Python напрямую:**
```bash
cd heroes-platform
python3 setup.py
```

**MCP конфигурация:**
```bash
cd heroes-platform
make setup-mcp
```

## Что происходит автоматически

✅ **Создается виртуальное окружение** (.venv)  
✅ **Устанавливаются все зависимости** из pyproject.toml  
✅ **Создаются необходимые директории** (logs, output, data, config)  
✅ **Копируются конфигурационные файлы** (pyproject.toml, .env)  
✅ **Настраивается MCP конфигурация** (.cursor/mcp.json)  
✅ **Запускаются тесты** для проверки установки  

## После установки

```bash
# Активировать окружение
source .venv/bin/activate  # Unix/Linux/macOS
# или
.venv\Scripts\activate.bat  # Windows

# Запустить MCP сервер
cd mcp_server && python run_mcp_server.py

# Запустить тесты
python run_tests.py
```

## Полезные команды

```bash
# Показать все доступные команды
make help

# Установить только dev зависимости
make install-dev

# Запустить линтинг
make lint

# Форматировать код
make format

# Очистить кэш
make clean
```

## Структура проекта

```
heroes-platform/
├── setup.py              # Автоматическая установка
├── install.sh            # Unix установка
├── install.bat           # Windows установка
├── Makefile              # Команды управления
├── package.json          # npm скрипты
├── README.md             # Подробная документация
├── MIGRATION_GUIDE.md    # Руководство по переносу
├── QUICK_START.md        # Это руководство
├── mcp_server/           # MCP сервер
├── tests/                # Тесты
├── src/                  # Исходный код
└── ...                   # Остальные компоненты
```

## Поддержка

- **Документация:** README.md
- **Миграция:** MIGRATION_GUIDE.md
- **CI/CD:** .github/workflows/ci.yml

---

**🎉 Готово! Все зависимости установлены автоматически из pyproject.toml**

