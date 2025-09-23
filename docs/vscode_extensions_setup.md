# VS Code Extensions Setup Guide

## 🎯 Цель документа

Настройка VS Code extensions для корректной работы с Parquet файлами и data preview в проекте 1C-extractor.

## 🔧 Настройки VS Code для Parquet файлов

### Основные настройки в `.vscode/settings.json`

```json
{
  "parquetViewer.backend": "arrow",
  "parquetViewer.outputFormat": "json", 
  "parquetViewer.maxRows": 1000,
  "parquetViewer.enablePreview": true,
  "files.associations": {
    "*.parquet": "parquet"
  },
  "workbench.editorAssociations": {
    "*.parquet": "parquetViewer"
  }
}
```

### Описание настроек

- **`parquetViewer.backend`**: Использует Apache Arrow для чтения Parquet файлов
- **`parquetViewer.outputFormat`**: Формат вывода данных (JSON)
- **`parquetViewer.maxRows`**: Максимальное количество строк для отображения
- **`parquetViewer.enablePreview`**: Включает preview для Parquet файлов
- **`files.associations`**: Связывает .parquet файлы с parquet типом
- **`workbench.editorAssociations`**: Назначает parquetViewer для открытия .parquet файлов

## 🚨 Решенные проблемы

### Проблема 1: "End of file expected" ошибка
**Причина:** VS Code пытался парсить Parquet файлы как JSON
**Решение:** Настройка правильных ассоциаций файлов и editor

### Проблема 2: Data preview не работает
**Причина:** Отсутствие конфигурации extension
**Решение:** Добавление настроек parquetViewer

### Проблема 3: Пустые таблицы в preview
**Причина:** Extension не знал, как обрабатывать Parquet файлы
**Решение:** Настройка backend и outputFormat

## 📋 Требуемые Extensions

### Обязательные extensions:
1. **Parquet Viewer** - для просмотра Parquet файлов
2. **Data Preview** - для preview данных
3. **Python** - для работы с Python кодом

### Установка extensions:
```bash
# Через VS Code Command Palette (Ctrl+Shift+P)
# Установить: Parquet Viewer, Data Preview, Python
```

## 🔍 Проверка настройки

### Команды для проверки:
```bash
# Проверить настройки VS Code
python3 -c "
import json
with open('.vscode/settings.json', 'r') as f:
    settings = json.load(f)
print('Parquet settings:', {k:v for k,v in settings.items() if 'parquet' in k.lower()})
"
```

### Ожидаемый результат:
- Parquet файлы открываются в parquetViewer
- Data preview показывает данные корректно
- Нет ошибок "End of file expected"

## 🚀 Дальнейшие улучшения

1. **Автоматизация настройки** - скрипт для настройки extensions
2. **Документация по troubleshooting** - решение типичных проблем
3. **Интеграция с CI/CD** - проверка настроек в pipeline

## 📚 Ссылки

- [Parquet Viewer Extension](https://marketplace.visualstudio.com/items?itemName=dvirtz.parquet-viewer)
- [Data Preview Extension](https://marketplace.visualstudio.com/items?itemName=RandomFractalsInc.vscode-data-preview)
- [VS Code Settings Documentation](https://code.visualstudio.com/docs/getstarted/settings)
