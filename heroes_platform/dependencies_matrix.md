# 📊 Dependencies Matrix - Heroes Platform Architecture

## 🎯 **Цель документа**
**JTBD:** Как разработчик, я хочу иметь четкое понимание архитектуры Heroes Platform и как проекты используют библиотеку, чтобы эффективно работать с существующей кодовой базой.

## 🏗️ **Архитектура Heroes Platform**

### **Heroes Platform как библиотека**
```
heroes_platform/                    # 🎯 ОСНОВНАЯ БИБЛИОТЕКА
├── heroes-mcp/                    # MCP серверы и команды (рефакторинг завершен)
│   ├── src/                      # Основной код MCP серверов
│   ├── workflows/                # Workflow модули
│   ├── tests/                    # Тесты MCP серверов
│   └── docs/                     # Документация MCP
├── src/                          # Исходный код библиотеки
├── tests/                        # Тесты библиотеки
├── scripts/                      # Скрипты и утилиты
├── config/                       # Конфигурации
└── ...                          # Другие компоненты платформы
```

### **Проекты в корне репозитория**
```
heroes-template/                   # Корневой репозиторий
├── heroes_platform/              # 🎯 БИБЛИОТЕКА (используется проектами)
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

## 🔄 **Принципы архитектуры**

### **1. Heroes Platform как библиотека**
- **heroes_platform/** содержит всю логику MCP серверов, workflow и инструментов
- Проекты используют heroes_platform как зависимость
- Все MCP команды и workflow находятся в heroes_platform
- Проекты НЕ содержат дублирующей функциональности

### **2. Проекты используют библиотеку**
- **Проекты** (папки с `[` и `]`) находятся в корне репозитория
- Каждый проект может использовать heroes_platform
- Проекты содержат только специфичную для них документацию и конфигурации
- Проекты НЕ содержат кода, который есть в heroes_platform

### **3. Стандарты и задачи**
- **[standards .md]/** - централизованная база стандартов
- **[todo · incidents]/** - управление задачами и инцидентами
- Все проекты следуют единым стандартам

## 🔧 **Интеграция проектов с Heroes Platform**

### **MCP Server Configuration**

**Автоматическая настройка:**
```bash
# Автоматическая настройка MCP конфигурации
cd heroes_platform
make setup-mcp
```

**Ручная настройка:**
```json
// .cursor/mcp.json - ПРАВИЛЬНАЯ КОНФИГУРАЦИЯ (локальная)
{
  "mcpServers": {
    "heroes-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/heroes_platform/heroes-mcp/src/heroes_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/heroes_platform"
      }
    }
  }
}
```

**⚠️ ВАЖНО: Все MCP серверы должны использовать .venv Python для консистентности и изоляции зависимостей**

**Архитектура конфигурации:**
- **Локальная конфигурация**: `.cursor/mcp.json` - ЕДИНСТВЕННЫЙ файл конфигурации
- **НЕ используем**: `~/.cursor/mcp.json` - системная конфигурация
- **Автоматическая настройка**: `make setup-mcp` создает локальную конфигурацию

### **Использование в проектах**
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

## 🎯 **Текущие проблемы и решения**

### **1. Правильная структура зависимостей**
- ✅ **Heroes Platform** - библиотека с MCP серверами
- ✅ **Проекты** - используют heroes_platform
- ✅ **Стандарты** - централизованы в [standards .md]/
- ✅ **Задачи** - централизованы в [todo · incidents]/

### **2. MCP Server Architecture**
- ✅ **Основной MCP сервер** - 136 команд в heroes_platform
- ✅ **Telegram MCP** - независимый сервер в heroes_platform/telegram-mcp/
- ✅ **Playwright MCP** - независимый сервер в heroes_platform/playwright-mcp/
- ✅ **N8N MCP** - независимый сервер в heroes_platform/n8n-mcp/

### **3. Workflow Integration**
- ✅ **54 workflow файла** в heroes_platform
- ✅ **TDD фреймворк** для качественного кода
- ✅ **AI QA фреймворк** для автоматического тестирования
- ✅ **Standards integration** для управления стандартами

## 📋 **Checklist для правильной архитектуры**

### **Heroes Platform (библиотека):**
- [x] Содержит все MCP серверы и команды
- [x] Содержит все workflow и инструменты
- [x] Содержит тесты и документацию
- [x] Может быть установлена как Python пакет
- [x] Имеет четкие API для использования проектами

### **Проекты (в корне):**
- [x] Используют heroes_platform как зависимость
- [x] Содержат только специфичную документацию
- [x] НЕ дублируют функциональность heroes_platform
- [x] Следуют единым стандартам
- [x] Имеют четкую структуру и назначение

### **Стандарты и задачи:**
- [x] Централизованы в [standards .md]/
- [x] Управляются через [todo · incidents]/
- [x] Применяются ко всем проектам
- [x] Имеют четкую версионность и историю

## 🚀 **Следующие шаги**

### **1. Обновление документации**
- [x] Обновлен README.md heroes_platform
- [x] Обновлен dependencies_matrix.md
- [ ] Обновить Registry Standard
- [ ] Обновить pyproject.toml
- [ ] Создать примеры использования в проектах

### **2. Проверка архитектуры**
- [ ] Убедиться что проекты не содержат дублирующего кода
- [ ] Проверить что все MCP команды в heroes_platform
- [ ] Валидировать что проекты используют heroes_platform
- [ ] Проверить конфигурации MCP серверов

### **3. Тестирование интеграции**
- [ ] Протестировать использование heroes_platform в проектах
- [ ] Проверить работу MCP серверов
- [ ] Валидировать workflow систему
- [ ] Проверить соответствие стандартам

## 🔗 **Ссылки на стандарты**

- **[Registry Standard](../../../[standards%20.md]/0.%20core%20standards/0.1%20registry%20standard%2015%20may%202025%201320%20CET%20by%20AI%20Assistant.md)** - для управления стандартами
- **[TDD Documentation Standard](../../../[standards%20.md]/4.%20dev%20·%20design%20·%20qa/4.1%20tdd%20documentation%20standard%2022%20may%202025%201830%20cet%20by%20ai%20assistant.md)** - для создания качественного кода
- **[FROM-THE-END Standard](../../../[standards%20.md]/1.%20process%20·%20goalmap%20·%20task%20·%20incidents%20·%20tickets%20·%20qa/1.4%20from-the-end.process.checkilst.md)** - для системного подхода

---

**Статус:** Архитектура обновлена, документация исправлена
**Следующий шаг:** Обновить Registry Standard и pyproject.toml
