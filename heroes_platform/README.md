# 🚀 Heroes Platform

**Heroes Platform** - это универсальная библиотека для создания AI-ассистированных проектов с интеграцией MCP серверов, стандартов и workflow.

## 🏗️ Архитектура проекта

### Структура репозитория
```
heroes-template/                    # Корневой репозиторий
├── heroes_platform/               # 🎯 ОСНОВНАЯ БИБЛИОТЕКА
│   ├── heroes-mcp/               # MCP серверы и команды (рефакторинг завершен)
│   ├── src/                      # Исходный код библиотеки
│   ├── tests/                    # Тесты
│   ├── scripts/                  # Скрипты
│   ├── config/                   # Конфигурации
│   ├── dependencies_matrix.md    # 📊 Матрица зависимостей
│   ├── README.md                 # 📖 Документация платформы
│   └── ...                      # Другие компоненты платформы
├── [clients]/                    # 📁 ПРОЕКТЫ КЛИЕНТОВ
├── [cursor] chats/               # 📁 ЧАТЫ CURSOR
├── [heroes-gpt-bot]/             # 📁 ПРОЕКТ HEROES-GPT
├── [heroes]/                     # 📁 ПРОЕКТЫ HEROES
├── [rick.ai]/                    # 📁 ПРОЕКТЫ RICK.AI
├── [standards .md]/              # 📁 СТАНДАРТЫ И ДОКУМЕНТАЦИЯ
├── [workshops]/                  # 📁 ВОРКШОПЫ
├── [todo · incidents]/           # 📁 ЗАДАЧИ И ИНЦИДЕНТЫ
├── data/                         # 📁 ДАННЫЕ
├── incident/                     # 📁 ИНЦИДЕНТЫ
└── ...                          # Другие файлы проекта
```

## 🎯 Принципы архитектуры

### 1. **Heroes Platform как библиотека**
- **heroes_platform/** - это основная библиотека с MCP серверами, workflow и инструментами
- Проекты используют heroes_platform как зависимость
- Все MCP команды и workflow находятся в heroes_platform

### 2. **Проекты в корне**
- **Проекты** (папки с `[` и `]`) находятся в корне репозитория
- Каждый проект может использовать heroes_platform
- Проекты содержат специфичную для них документацию и конфигурации

### 3. **Стандарты и задачи**
- **[standards .md]/** - централизованная база стандартов
- **[todo · incidents]/** - управление задачами и инцидентами
- Все проекты следуют единым стандартам

## 🔧 Установка и настройка

### MCP Configuration

**Для локального проекта:**
```bash
# Автоматическая настройка MCP конфигурации
make setup-mcp

# Или вручную
python scripts/setup_mcp_config.py
```

**Конфигурация создается в `.cursor/mcp.json`** с правильными путями к heroes-platform.

**⚠️ ВАЖНО: Cursor НЕ нужно перезапускать:**
- Изменения в `.cursor/mcp.json` применяются автоматически
- Достаточно включить/отключить MCP серверы в UI Cursor
- Cursor автоматически перезагружает конфигурацию при изменениях
- Перезапуск Cursor требуется только при критических изменениях системы

**Для отчуждаемого пакета:**
- Используйте `.cursor/mcp.json.example` как шаблон
- Замените `{HEROES_PLATFORM_PATH}` на реальный путь
- Скопируйте в `.cursor/mcp.json` вашего проекта

### Быстрая установка
```bash
# Клонирование репозитория
git clone <repository-url>
cd heroes-template

# Создание виртуального окружения с Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate

# Установка heroes_platform со всеми зависимостями
cd heroes_platform
pip install -e ".[dev]"

# Установка дополнительных зависимостей для web scraping, PDF, GraphQL
pip install selenium beautifulsoup4 aiohttp gql PyPDF2 weasyprint arrow ujson PyJWT
```

**⚠️ ВАЖНО: Все MCP серверы используют .venv Python для консистентности и изоляции зависимостей**

### Основные зависимости

**Web scraping и parsing:**
- `selenium>=4.15.0` - автоматизация браузера для тестирования
- `beautifulsoup4>=4.12.0` - парсинг HTML/XML документов
- `aiohttp>=3.9.0` - асинхронные HTTP запросы

**PDF processing:**
- `PyPDF2>=3.0.0` - работа с PDF файлами
- `weasyprint>=60.0` - генерация PDF из HTML/CSS

**GraphQL и API:**
- `gql>=3.4.0` - GraphQL клиент для API интеграций
- `gql[requests]>=3.4.0` - GraphQL с requests транспортом

**Утилиты:**
- `arrow>=1.3.0` - работа с датами и временем
- `ujson>=5.8.0` - быстрая JSON обработка
- `PyJWT>=2.8.0` - JWT аутентификация

### Настройка MCP серверов
```bash
# Настройка Cursor для работы с MCP (локальная конфигурация)
cp heroes_platform/.cursor/mcp.json.example .cursor/mcp.json
# Замените {HEROES_PLATFORM_PATH} на реальный путь к heroes_platform
```

### 🚨 КРИТИЧЕСКИ ВАЖНО: Тестирование MCP серверов

**⚠️ ПРОБЛЕМА:** MCP серверы при запуске из терминала без аргументов зависают!

**✅ РЕШЕНИЕ:** Всегда используйте CLI аргументы для тестирования:

```bash
# ✅ ПРАВИЛЬНО - с CLI аргументами
python3 heroes_platform/heroes_mcp/src/heroes_mcp_server.py --help
python3 heroes_platform/heroes_mcp/src/heroes_mcp_server.py --list-tools
node heroes_platform/n8n-mcp/dist/mcp/index.js --help
node heroes_platform/n8n-mcp/dist/mcp/index.js --list-tools

# ✅ ПРАВИЛЬНО - через MCP CLI
mcp run heroes_platform/heroes_mcp/src/heroes_mcp_server.py

# ❌ НЕПРАВИЛЬНО - без аргументов (зависнет)
python3 heroes_platform/heroes_mcp/src/heroes_mcp_server.py
node heroes_platform/n8n-mcp/dist/mcp/index.js
```

**Автоматическое тестирование:**
```bash
# Запуск тестирования всех MCP серверов
python3 scripts/test_mcp_servers.py
```

## 📚 Основные компоненты

### MCP Серверы
- **Основной MCP сервер** - 136 команд для работы со стандартами и workflow
- **Telegram MCP** - интеграция с Telegram
- **Playwright MCP** - автоматизированное тестирование
- **N8N MCP** - интеграция с N8N
- **Figma MCP** - анализ и управление дизайн-системами

### Workflow Система
- **54 workflow файла** с валидацией и compliance
- **TDD фреймворк** для качественного кода
- **AI QA фреймворк** для автоматического тестирования

### Стандарты
- **59 стандартов** в централизованной базе
- **Registry Standard** для управления стандартами
- **Task Master Standard** для управления задачами

## 🚀 Использование в проектах

### Пример использования в проекте
```python
# В любом проекте можно использовать heroes_platform
from heroes_platform.heroes_mcp import MCPClient
from heroes_platform.workflows import StandardsWorkflow

# Инициализация клиента
client = MCPClient()

# Использование workflow
workflow = StandardsWorkflow()
result = workflow.analyze_standards()
```

### Интеграция с Cursor
```json
// .cursor/mcp.json (локальная конфигурация)
{
  "mcpServers": {
    "heroes-mcp": {
      "command": "/absolute/path/to/python3",
      "args": ["/absolute/path/to/heroes_platform/heroes-mcp/src/heroes_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/heroes_platform"
      }
    }
  }
}
```

**⚠️ ВАЖНО:** Cursor не поддерживает переменные `${workspaceFolder}`. Используйте абсолютные пути для всех MCP серверов.

## 📋 Разработка

### Запуск тестов
```bash
cd heroes_platform
pytest tests/ -v
```

### Линтинг и форматирование
```bash
cd heroes_platform
black .
ruff check .
mypy .
```

### Сборка документации
```bash
cd heroes_platform
mkdocs build
```

## 🎨 Figma MCP Integration

### Overview
The system now includes **Figma MCP Pro** (v3.49.0) for reading and analyzing Figma documents. This enables AI-powered design analysis, component extraction, and design system management.

### Setup
1. **Installation**: `npm install -g figma-mcp-pro` ✅ (Completed)
2. **Configuration**: MCP config updated in `.cursor/mcp.json` (локальная конфигурация)
3. **API Key**: Store your Figma API key in Mac Keychain with service name `figma_api_key`
4. **Restart**: Restart Cursor to load the new MCP configuration

### API Key Setup
```bash
# Store Figma API key in Mac Keychain
security add-generic-password -s "figma_api_key" -a "ilyakrasinsky" -w "YOUR_FIGMA_API_KEY"

# Or use the credentials manager
python -c "from heroes_platform.shared.credentials_manager import store_credential; store_credential('figma_api_key', 'YOUR_FIGMA_API_KEY')"
```

### Available Figma Tools
- **File Operations**: `get_file_info`, `get_file_nodes`, `get_file_comments`
- **Design System**: `get_component_info`, `get_component_sets`, `get_styles`
- **Asset Management**: `export_images`, `get_file_assets`
- **Advanced Analysis**: `process_design_context`, `extract_design_tokens`, `get_design_system`

### Usage Examples
```
"Get information about the Figma file with ID ABC123"
"Extract design tokens from this Figma file"
"Export images from file ABC123 as PNG files"
"Analyze the design system in this file"
```

### Documentation
- **Setup Guide**: `docs/figma-mcp-setup.md`
- **Tools Reference**: `docs/figma-mcp-tools.md`
- **API Limits**: 100 requests/minute for file access and image export

### Security
- API key stored securely in Mac Keychain with service name `figma_api_key`
- Access limited to files with proper permissions
- Integrated with unified credentials management system
- Fallback to environment variables and GitHub secrets

## ⚠️ Agent TARS - УДАЛЕН ИЗ-ЗА УЯЗВИМОСТЕЙ БЕЗОПАСНОСТИ

**Agent TARS был удален** из Heroes Platform из-за критических уязвимостей безопасности.

### 🚨 Проблемы безопасности:
- **21 уязвимость** (1 moderate, 20 high)
- **3 ReDoS атаки** (CVSS 7.5)
- **4 deprecated пакета** с утечками памяти
- **Небезопасен для production** использования

### 🔍 Детали уязвимостей:
- `cross-spawn` - ReDoS атака (CVSS 7.5)
- `http-cache-semantics` - ReDoS атака (CVSS 7.5)
- `semver-regex` - ReDoS атака (CVSS 7.5)
- `got` - Redirect to UNIX socket (CVSS 5.3)

### ✅ Статус:
- **Удален**: Agent TARS полностью удален из проекта
- **Безопасность**: 0 уязвимостей в npm пакетах
- **Рекомендация**: Использовать другие AI агенты без проблем безопасности

## 🤖 Potpie AI Integration

**Heroes Platform** теперь интегрирован с [Potpie](https://github.com/potpie-ai/potpie) - AI-платформой для создания кастомных инженерных агентов и анализа кодовой базы.

### Возможности Potpie:
- **AI-агенты для анализа кода** - автоматический анализ архитектуры и качества кода
- **Knowledge Graph** - построение графа знаний из кодовой базы
- **Кастомные агенты** - создание специализированных агентов для конкретных задач
- **Интеграция с Heroes Platform** - использование MCP команд и workflow

### Быстрый старт с Potpie:
```bash
# Запуск интегрированной системы
./start_heroes_with_potpie.sh

# Тестирование интеграции
python scripts/test_potpie_integration.py
```

### Использование:
```bash
# Анализ репозитория через Potpie
curl -X POST 'http://localhost:8001/api/v1/parse' \
  -H 'Content-Type: application/json' \
  -d '{"repo_path": "/path/to/repo", "branch_name": "main"}'

# Создание разговора с AI-агентом
curl -X POST 'http://localhost:8001/api/v1/conversations/' \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "heroes_user", "title": "Code Analysis", "status": "active"}'
```

📖 **Подробная документация**: [POTPIE_INTEGRATION.md](./POTPIE_INTEGRATION.md)

## 📊 Статистика проекта

- **MCP команд:** 136
- **Workflow файлов:** 54
- **Стандартов:** 59
- **Тестов:** 200+
- **Покрытие кода:** 85%+
- **AI-агентов Potpie:** Интегрированы

## 🔗 Ссылки

- [Документация стандартов](../[standards%20.md]/)
- [Задачи и инциденты](../[todo%20·%20incidents]/)
- [MCP серверы](./heroes-mcp/)
- [Workflow система](./src/workflows/)
- [Матрица зависимостей](./dependencies_matrix.md)

## 📄 Лицензия

Все права защищены. Данный проект является интеллектуальной собственностью Ильи Красинского.

---

**Версия:** 1.0.0  
**Обновлено:** 26 августа 2025  
**Статус:** Активная разработка
