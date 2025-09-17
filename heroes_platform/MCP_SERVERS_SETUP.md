# MCP Серверы - Установка и Настройка

## Обзор

В проекте настроены два локальных MCP сервера:

1. **n8n-mcp** - сервер для работы с n8n workflows
2. **jira-mcp** - сервер для работы с Atlassian Jira

## Установленные серверы

### 1. n8n-mcp сервер

**Расположение:** `heroes-platform/n8n-mcp/`

**Источник:** https://github.com/czlonkowski/n8n-mcp.git

**Функциональность:**
- Создание и управление n8n workflows
- Поиск и валидация n8n nodes
- Управление выполнением workflows
- Интеграция с n8n API

**Конфигурация в Cursor:**
```json
"n8n-mcp": {
  "command": "node",
  "args": ["dist/index.js"],
  "cwd": "heroes-platform/n8n-mcp"
}
```

### 2. jira-mcp сервер

**Пакет:** `@aashari/mcp-server-atlassian-jira`

**Функциональность:**
- Управление проектами Jira
- Поиск и управление issues
- Работа с комментариями и worklogs
- JQL запросы

**Конфигурация в Cursor:**
```json
"jira-mcp": {
  "command": "npx",
  "args": ["@aashari/mcp-server-atlassian-jira"]
}
```

## Обновление серверов

### n8n-mcp

```bash
cd heroes-platform/n8n-mcp
git pull origin main
npm install
npm run build
```

### jira-mcp

```bash
npm update -g @aashari/mcp-server-atlassian-jira
```

## Тестирование

Запустите тестовый скрипт для проверки работы серверов:

```bash
cd heroes-platform
python3 test_n8n_mcp.py
```

## Использование в Cursor

После настройки MCP серверов в `.cursor/mcp.json`, вы можете использовать их инструменты в Cursor:

### n8n-mcp инструменты:
- `n8n_create_workflow` - создание новых workflows
- `n8n_get_workflow` - получение информации о workflow
- `n8n_list_workflows` - список workflows
- `n8n_validate_workflow` - валидация workflows
- `search_nodes` - поиск n8n nodes
- `get_node_essentials` - получение информации о node

### jira-mcp инструменты:
- `ls_projects` - список проектов
- `ls_issues` - поиск issues
- `get_issue` - получение информации об issue
- `add_comment` - добавление комментария
- `add_worklog` - добавление worklog

## Требования

- Node.js >= 20.15.0
- npm
- Python 3.x (для тестового скрипта)

## Устранение неполадок

### n8n-mcp не запускается
1. Проверьте, что Node.js версии >= 20.15.0
2. Пересоберите проект: `npm run build`
3. Проверьте зависимости: `npm install`

### jira-mcp не работает
1. Переустановите пакет: `npm install -g @aashari/mcp-server-atlassian-jira`
2. Проверьте права доступа к глобальным пакетам

### Проблемы с конфигурацией Cursor
1. Перезапустите Cursor
2. Проверьте синтаксис JSON в `.cursor/mcp.json`
3. Убедитесь, что пути к серверам корректны

## Дополнительные ресурсы

- [n8n-mcp документация](https://github.com/czlonkowski/n8n-mcp)
- [jira-mcp документация](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-jira)
- [MCP Protocol](https://modelcontextprotocol.io/)
