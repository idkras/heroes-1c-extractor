# API Документация

Этот раздел содержит документацию по API маршрутам Advising Platform.

## Основные конечные точки

### Статус системы

Проверка текущего статуса системы.

```
GET /api/status
```

Пример ответа:
```json
{
  "components": {
    "api": {
      "status": "running"
    }, 
    "cache": {
      "status": "running"
    }, 
    "sync": {
      "status": "running"
    }
  }, 
  "file_reorganization": {
    "status": "completed", 
    "timestamp": "2025-05-15T21:54:00Z"
  }, 
  "status": "ok", 
  "uptime": "1d 2h 34m", 
  "version": "1.0.0"
}
```

### Статус реорганизации файлов

Получение информации о прогрессе реорганизации файловой структуры.

```
GET /api/reorganization/status
```

Пример ответа:
```json
{
  "completion_percentage": 87.5,
  "files_relocated": 5,
  "last_updated": "2025-05-15T21:56:05Z",
  "maintainer": "AI Assistant",
  "readme_files_created": 5,
  "started_at": "2025-05-15T21:00:00Z",
  "status": "in_progress",
  "tasks": [
    {
      "name": "process_incidents.py",
      "new_path": "advising_platform/scripts/incidents/process_incidents.py",
      "old_path": "/process_incidents.py",
      "status": "completed"
    },
    {
      "name": "test_bidirectional_sync.py",
      "new_path": "advising_platform/scripts/tests/test_bidirectional_sync.py",
      "old_path": "/test_bidirectional_sync.py",
      "status": "completed"
    },
    // другие задачи...
  ]
}
```

### Стандарты

Получение списка стандартов.

```
GET /api/standards
```

### Гипотезы

Получение списка гипотез.

```
GET /api/hypotheses
```

### Индексация

Поиск по индексированным документам.

```
GET /api/index/search?query=...
```

### Задачи (Todo)

Получение списка задач.

```
GET /api/todo/items
```

## Структура маршрутов API

API маршруты организованы в соответствии с модульной структурой:

```
advising_platform/src/api/
├── routes/                # Новая структура маршрутов
│   ├── status.py          # Маршруты для проверки статуса
│   ├── reorganization.py  # Маршруты для информации о реорганизации
│   └── ...                # Другие маршруты
├── standards_routes.py    # Старая структура (будет перемещена)
├── hypothesis_routes.py   # Старая структура (будет перемещена)
└── ...
```

## Использование API в клиентских приложениях

```javascript
// Пример получения статуса системы
fetch('/api/status')
  .then(response => response.json())
  .then(data => console.log(data));

// Пример получения статуса реорганизации
fetch('/api/reorganization/status')
  .then(response => response.json())
  .then(data => console.log(data));
```