# Директория для данных платформы

Эта директория содержит различные данные, используемые платформой.

## Структура

```
advising_platform/data/
├── logs/           # Журналы логов
│   ├── cache_validation.log      # Логи валидации кэша
│   ├── data_migration.log        # Логи миграции данных
│   ├── directory_move.log        # Логи перемещения директорий
│   └── todo_validation.log       # Логи валидации задач
├── test_results/   # Результаты тестов
│   ├── bidirectional_sync_test_results.json  # Результаты тестов синхронизации
│   └── cache_validation_report.json          # Отчет о валидации кэша
└── ...
```

## Журналы логов

Директория `logs/` содержит журналы логов различных компонентов системы:

- `cache_validation.log` - Логи процесса валидации кэша
- `data_migration.log` - Логи процесса миграции данных
- `directory_move.log` - Логи процесса перемещения директорий
- `todo_validation.log` - Логи процесса валидации задач

## Результаты тестов

Директория `test_results/` содержит результаты выполнения тестов в JSON-формате:

- `bidirectional_sync_test_results.json` - Результаты тестов синхронизации кэша
- `cache_validation_report.json` - Подробный отчет о валидации кэша

## Доступ к данным

Рекомендуется использовать относительные пути при доступе к данным:

```python
import os

# Получение пути к директории данных
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Получение пути к конкретному файлу
log_file = os.path.join(DATA_DIR, 'logs', 'cache_validation.log')
```