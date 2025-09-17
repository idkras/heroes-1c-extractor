# n8n Integration Documentation

## Обзор

Интеграция с n8n позволяет управлять workflow автоматизации через MCP команды. Основана на [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) от czlonkowski.

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install httpx pydantic
```

### 2. Конфигурация n8n

Создайте файл `config/n8n_config.json`:

```json
{
  "n8n": {
    "base_url": "http://localhost:5678",
    "api_key": "your_api_key_here",
    "username": "",
    "password": "",
    "timeout": 30
  }
}
```

### 3. Инициализация интеграции

```python
# Инициализация с API ключом
n8n_init_integration(
    base_url="http://localhost:5678",
    api_key="your_api_key_here"
)

# Или с basic auth
n8n_init_integration(
    base_url="http://localhost:5678",
    username="admin",
    password="password"
)
```

## Доступные команды

### Основные команды

#### `n8n_health_check()`
Проверка состояния n8n сервера.

**Возвращает:**
```json
{
  "status": "healthy",
  "n8n_version": "1.0.0",
  "response_time": 0.123
}
```

#### `n8n_list_workflows(limit: int = 50, offset: int = 0)`
Получение списка workflow.

**Параметры:**
- `limit`: Максимальное количество workflow
- `offset`: Смещение для пагинации

**Возвращает:**
```json
{
  "workflows": [...],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

#### `n8n_get_workflow(workflow_id: str)`
Получение конкретного workflow по ID.

#### `n8n_create_workflow(workflow_data: str)`
Создание нового workflow.

**Параметры:**
- `workflow_data`: JSON строка с данными workflow

#### `n8n_update_workflow(workflow_id: str, workflow_data: str)`
Обновление существующего workflow.

#### `n8n_delete_workflow(workflow_id: str)`
Удаление workflow.

### Управление состоянием

#### `n8n_activate_workflow(workflow_id: str)`
Активация workflow.

#### `n8n_deactivate_workflow(workflow_id: str)`
Деактивация workflow.

### Выполнение workflow

#### `n8n_trigger_workflow(workflow_id: str, data: str = "{}")`
Запуск workflow через webhook.

**Параметры:**
- `workflow_id`: ID workflow
- `data`: JSON строка с данными для передачи

#### `n8n_get_executions(workflow_id: str = "", limit: int = 50)`
Получение списка выполнений.

#### `n8n_get_execution(execution_id: str)`
Получение конкретного выполнения по ID.

## Примеры использования

### 1. Создание простого workflow

```python
# Создаем простой workflow с webhook
workflow_data = {
    "name": "Test Workflow",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "test",
                "responseMode": "responseNode"
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [240, 300]
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "{\"message\": \"Hello from n8n!\"}"
            },
            "name": "Response",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [460, 300]
        }
    ],
    "connections": {
        "Webhook": {
            "main": [[{"node": "Response", "type": "main", "index": 0}]]
        }
    },
    "active": False
}

result = n8n_create_workflow(json.dumps(workflow_data))
```

### 2. Интеграция с HeroesGPT

```python
# Инициализируем интеграцию
n8n_init_integration(
    base_url="http://localhost:5678",
    api_key="your_api_key"
)

# Создаем workflow для анализа лендинга
with open("examples/n8n_workflows/heroes_gpt_analysis.json", "r") as f:
    workflow_data = f.read()

result = n8n_create_workflow(workflow_data)
workflow_id = result["id"]

# Активируем workflow
n8n_activate_workflow(workflow_id)

# Запускаем анализ
trigger_data = {
    "url": "https://example.com",
    "analysis_depth": "full",
    "business_context": {"type": "saas"}
}

result = n8n_trigger_workflow(workflow_id, json.dumps(trigger_data))
```

### 3. Мониторинг выполнений

```python
# Получаем список выполнений
executions = n8n_get_executions(workflow_id="your_workflow_id", limit=10)

# Получаем детали конкретного выполнения
execution_details = n8n_get_execution(execution_id="execution_id")
```

## Интеграция с существующими workflow

### HeroesGPT Analysis Workflow

Создан готовый workflow для интеграции с HeroesGPT анализом лендингов:

1. **Webhook Trigger**: Принимает данные для анализа
2. **Data Extraction**: Извлекает и валидирует входные данные
3. **HeroesGPT API**: Отправляет запрос к API анализа
4. **Results Processing**: Обрабатывает и форматирует результаты
5. **Response**: Возвращает результат анализа

### Standards Management Workflow

Workflow для автоматического обновления стандартов:

1. **Webhook Trigger**: Принимает данные об изменениях
2. **Validation**: Проверяет корректность данных
3. **Standards Update**: Обновляет соответствующие стандарты
4. **Notification**: Отправляет уведомления об изменениях

## Обработка ошибок

Все команды возвращают JSON с информацией об ошибках:

```json
{
  "error": "Описание ошибки",
  "details": "Дополнительная информация"
}
```

## Безопасность

### Аутентификация

Поддерживаются два метода аутентификации:

1. **API Key**: Рекомендуется для production
2. **Basic Auth**: Для простых случаев

### Валидация данных

Все входные данные валидируются:
- JSON формат
- Обязательные поля
- Типы данных

## Мониторинг и логирование

Все операции логируются с уровнем INFO и выше. Ошибки логируются с уровнем ERROR.

## Ограничения

1. **Rate Limiting**: Соблюдайте ограничения n8n API
2. **Timeout**: Настройте таймауты для длительных операций
3. **Memory**: Большие workflow могут потребовать больше памяти

## Troubleshooting

### Проблемы подключения

1. Проверьте URL n8n сервера
2. Убедитесь в правильности аутентификации
3. Проверьте сетевые настройки

### Проблемы с workflow

1. Валидируйте JSON структуру workflow
2. Проверьте типы узлов
3. Убедитесь в корректности соединений

### Проблемы с выполнением

1. Проверьте активность workflow
2. Убедитесь в наличии webhook узлов
3. Проверьте логи выполнения

## Дополнительные ресурсы

- [n8n Documentation](https://docs.n8n.io/)
- [n8n API Reference](https://docs.n8n.io/api/)
- [n8n-mcp Repository](https://github.com/czlonkowski/n8n-mcp)
