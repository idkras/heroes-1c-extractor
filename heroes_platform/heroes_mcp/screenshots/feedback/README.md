# Screenshots Feedback Directory

## Структура хранения скриншотов для фидбека

### Формат именования файлов:
```
{task_name}_{YYYYMMDD}_{HHMMSS}.jpg
```

### Примеры:
- `cleanshot_refactoring_20250826_113900.jpg`
- `telegram_integration_20250826_114500.jpg`
- `mcp_server_testing_20250826_120000.jpg`

### Организация по датам:
```
screenshots/feedback/
├── 2025-08-26/
│   ├── cleanshot_refactoring_20250826_113900.jpg
│   └── telegram_integration_20250826_114500.jpg
├── 2025-08-27/
│   └── new_feature_20250827_090000.jpg
└── README.md
```

### Метаданные:
- **Дата**: YYYY-MM-DD
- **Время**: HH:MM:SS
- **Задача**: Описательное название задачи
- **Контекст**: Краткое описание контекста фидбека

### Автоматическое создание папок:
Система автоматически создает папки по датам при сохранении скриншотов.
